import urllib
import urllib.parse
import urllib.request
import urllib.error
import csv
import os
import datetime
import time
import json


class WhiskKpi(object):
    filename = "exports/whisk_kpi.csv"
    ENDPOINT = 'https://admin.whisk.com/api'

    def request(self, methods, params, format='json'):
        request_url = '/'.join([self.ENDPOINT] + methods) + '?' + self.unicode_urlencode(params)
        request = urllib.request.Request(request_url)
        # Add whisk admin session below
        request.add_header("WhiskAdminSessionId", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        request = urllib.request.urlopen(request)
        data = request.read().decode('utf-8')
        return json.loads(data)

    def unicode_urlencode(self, params):
        if isinstance(params, dict):
            params = params.items()
        for i, param in enumerate(params):
            if isinstance(param[1], list):
                params[i] = (param[0], json.dumps(param[1]),)

        return urllib.parse.urlencode([(k, v.encode('utf-8') or v)
                                      for k, v in params])
    def check_dir(self):
        dir = os.path.dirname(self.filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return self.filename

    def print_to_csv(self, dataFile, data):
        writer = csv.writer(dataFile, lineterminator='\n')
        for row in data:
            writer.writerows([row])


if __name__ == '__main__':
    languages = ["en", "en-us", "en-gb", "es", "es-ar", "es-mx",
                 "fr", "fr-ca", "de", "nl"]
    statusAnno = ["AcceptedAsBest", "AnnotationProposed",
                  "Flagged", "NothingProposed"]

    api = WhiskKpi()
    with open(api.check_dir(), "a") as filename:
        data = []
    # initiate cycle of data and writing data
        for language in languages:
            rdata = list()
            rdata.append(str(datetime.date.today()))
            overallTotal = api.request(['recipeingredients'],
                                       {
                                           'language': language,
                                           'limit': '1',
                                           'offset': '0'
            })
            time.sleep(1)
            rdata.append(language)
            rdata.append(overallTotal['paging']['total'])
            for status in statusAnno:
                recipeIngredient = api.request(['recipeingredients'],
                                               {
                                                   'language': language,
                                                   'status': status,
                                                   'limit': '1',
                                                   'offset': '0'
                })
                rdata.append(recipeIngredient['paging']['total'])
                time.sleep(1)
            data.append(rdata)
            del rdata
        api.print_to_csv(filename, data)
