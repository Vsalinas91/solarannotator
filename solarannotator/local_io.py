import os

from .io import ImageSet
from goessolarretriever import Retriever, Satellite, Product
from goessolarretriever.fetch import date_range, NameParser
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import namedtuple
from astropy.io import fits
from sunpy.coordinates import SphericalScreen

""" how to reference in GUI
import .local_io as local_io
local_io.LOCAL_DATA_PATH = USER_PROVIDED_VAR
"""

Image = namedtuple('Image', 'data header')


class LocalRetriever(Retriever):
    def __init__(self, working_dir):
        super().__init__()
        self.working_dir = working_dir

    @staticmethod
    def _format_url(working_dir: str, satellite: Satellite, product: Product, date: datetime) -> str:
        satellite_str = str.lower(str(satellite).split(".")[1])
        product_str = str(product).split(".")[1].replace("_", "-")
        level = product_str.split("-")[1]
        date_str = date.strftime("%Y/%m/%d/")
        return "/".join([working_dir, satellite_str, level, "data", product_str, date_str])

    @staticmethod
    def _fetch_page(url: str, parser):
        import glob
        entries = glob.glob(os.path.join(url, "*"))

        def get_file_info(file_path):
            file_name = os.path.basename(file_path)
            stat = os.stat(file_path)
            date_edited = datetime.fromtimestamp(stat.st_mtime)
            date_begin, date_end = parser.get_dates(file_name)
            file_size = f"{round(stat.st_size / 1024**2, 1)}M"
            return {'file_name': file_name, 'date_begin': date_begin, 'date_end': date_end,
                    'date_edited': date_edited, 'file_size': file_size, 'url': file_path}

        results = list(map(get_file_info, entries))
        df = pd.DataFrame(results)
        return df

    def search(self, working_dir, satellite: Satellite, product,
               start, end=None):
        if end is None:
            end = datetime(start.year, start.month, start.day, 23, 59, 59)

        results = pd.DataFrame()
        for day in date_range(start, end):
            name_parser = NameParser(satellite, product)
            url = self._format_url(working_dir, satellite, product, day)
            page = self._fetch_page(url, name_parser)
            results = pd.concat([results, page], ignore_index=True)
        return results

    def retrieve(self, results, save_directory):
        pass

    def retrieve_nearest(self, satellite, product, date):
        df = self.search(self.working_dir, satellite, product, date)
        try:
            best_index = np.argmin(np.abs(df['date_begin'] - date))
        except KeyError:
            raise RuntimeError("Data does not exist for the time {}".format(date))
        return df.iloc[best_index]['url']

class LocalImageSet(ImageSet):
    @staticmethod
    def retrieve(working_dir, satellite, date):
        full_set = LocalImageSet._load_suvi_composites(working_dir, satellite, date)
        full_set['gong'] = ImageSet._load_gong_image(date, full_set['195'])
        return ImageSet(full_set)

    @staticmethod
    def _load_gong_image(date, suvi_195_image):
        # Find an image and download it
        results = Fido.search(a.Time(date - timedelta(hours=1), date + timedelta(hours=1)),
                              a.Wavelength(6563 * u.Angstrom), a.Source("GONG"))
        selection = results[0][len(results[0]) // 2]  # only download the middle image
        downloads = Fido.fetch(selection)
        with fits.open(downloads[0]) as hdul:
            gong_data = hdul[1].data
            gong_head = hdul[1].header

        # update the header to actually load in a SunPy map
        gong_head['CTYPE1'] = "HPLN-TAN"
        gong_head['CTYPE2'] = "HPLT-TAN"
        gong_head['CUNIT1'] = "arcsec"
        gong_head['CUNIT2'] = "arcsec"
        # number below from SunPy discussions: https://github.com/sunpy/sunpy/issues/6656#issuecomment-1344413011
        gong_head['CDELT1'] = 1.082371820584223
        gong_head['CDELT2'] = 1.082371820584223

        # Load as a map
        gong_map = sunpy.map.Map(gong_data, gong_head)
        suvi_map = sunpy.map.Map(suvi_195_image.data, suvi_195_image.header)
        suvi_head = suvi_195_image.header

        with SphericalScreen(suvi_map.observer_coordinate, only_off_disk=True):
            out = gong_map.reproject_to(suvi_head)

        return Image(out.data, dict(out.meta))

    @staticmethod
    def _load_suvi_composites(working_dir, satellite, date):
        satellite = getattr(Satellite, satellite)
        products = {"94": Product.suvi_l2_ci094,
                    "131": Product.suvi_l2_ci131,
                    "171": Product.suvi_l2_ci171,
                    "195": Product.suvi_l2_ci195,
                    "284": Product.suvi_l2_ci284,
                    "304": Product.suvi_l2_ci304}
        composites = {}
        r = LocalRetriever(working_dir)
        for wavelength, product in products.items():
            fn = r.retrieve_nearest(satellite, product, date)
            with fits.open(fn) as hdus:
                data = hdus[1].data
                header = hdus[1].header
                composites[wavelength] = Image(data, header)
        return composites



class NameParser:
    suvi_ci = {Product.suvi_l2_ci094,
               Product.suvi_l2_ci131,
               Product.suvi_l2_ci171,
               Product.suvi_l2_ci195,
               Product.suvi_l2_ci284,
               Product.suvi_l2_ci304}

    suvi_lib = {Product.suvi_l1b_fe094,
                Product.suvi_l1b_fe131,
                Product.suvi_l1b_fe171,
                Product.suvi_l1b_fe195,
                Product.suvi_l1b_fe284,
                Product.suvi_l1b_he304}

    def __init__(self, satellite: Satellite, product: Product):
        self.satellite = satellite
        self.product = product

    def get_dates(self, name):
        """
        Overall method to get the date and time from a filename string
        :param name: filename extracted from web page
        :return: start and end times of the observation
        """
        if self.product in NameParser.suvi_ci:
            return NameParser._get_dates_suvi_ci(name)
        elif self.product in NameParser.suvi_lib:
            return NameParser._get_dates_suvi_l1b(name)
        else:
            return None, None

    @staticmethod
    def _get_dates_suvi_ci(name):
        """
        Filename parser for Suvi Composite Image data
        :param name: filename
        :return: start and end date
        """
        _, product_str, satellite_str, start_str, end_str, _ = name.split("_")
        start = datetime.strptime(start_str, "s%Y%m%dT%H%M%SZ")
        end = datetime.strptime(end_str, "e%Y%m%dT%H%M%SZ")
        return start, end

    @staticmethod
    def _get_dates_suvi_l1b(name):
        """
        Filename parser for Suvi Composite Image data
        :param name: filename
        :return: start and end date
        """
        _, product_str, satellite_str, start_str, end_str, _ = name.split("_")
        start = datetime.strptime(start_str[:-1], "s%Y%j%H%M%S")
        end = datetime.strptime(end_str[:-1], "e%Y%j%H%M%S")
        return start, end

def date_range(start, end):
    # Truncate the hours, minutes, and seconds
    sdate = datetime(start.year, start.month, start.day)
    edate = datetime(end.year, end.month, end.day)

    # compute all dates in that difference
    delta: timedelta = edate - sdate
    return [start + timedelta(days=i) for i in range(delta.days + 1)]
