import json
import os


class DistrictConverter:
    def __init__(self):
        self.districts = self.__read_district_file()
    
    def __read_district_file(self):
        json_file_path = 'district.json'

        with open(json_file_path, 'r') as f:
            return json.loads(f.read())

    def get_data(self):
        return self.districts

    def get_si_do_name(self, si_do):
        for district in self.districts:
            if si_do in district['si_do_name']:
                return district['si_do_name']

    def get_si_do_code(self, si_do_name):
        for district in self.districts:
            if si_do_name in district['si_do_name']:
                return district['sigungu']

    def get_sigungu_list(self, si_do_code, sigungu_name):
        sigungu_list = []
        sigungu_data = self.get_sigungu(si_do_code)
        for sigungu in sigungu_data:
            if sigungu_name in sigungu['sigungu_name']:
                sigungu_list.append(sigungu)

        return sigungu_list

if __name__ == '__main__':
    c = DistrictConverter()
    print(c.get_data())