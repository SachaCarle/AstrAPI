import requests, logging, sys, json

def var_dump(*args):
    logging.info(str(args))

class AstrAPIWrapper:

    def __init__(self, base_url):
        self.clean()
        self.base_url = base_url

    def setCurrentEndpoint(self, endpoint, clean=False, resource=False):
        if clean:
            self.clean()
        self.endpoint = endpoint
        self.resource = resource

    def addBodyParam(self, name):
        self.barams[name] = None

    def addParam(self, name):
        self.params[name] = None

    def setParam(self, name, value):
        if name in self.params.keys():
            self.params[name] = value
        elif name in self.barams.keys():
            self.barams[name] = value

    def clean(self):
        self.endpoint = None
        self.r = None
        self.params = dict()
        self.barams = dict()
        self.resource = False

    def parse_failed(self):
        var_dump(self.r.raw.data)
        var_dump(self.r.content)
        var_dump(self.r.text)
        var_dump(json.loads(self.r.text))
        raise Exception('Failed to parse.')

    def parse(self):
        try:
            res = self.r.json()
            if res is None:
                res = json.loads(self.r.raw.data)
        except Exception as e:
            self.parse_failed()
        else:
            if res == None:
                self.parse_failed()
            return res

    def get(self):
        assert self.endpoint != None
        self.r = requests.get(self.url())
        return self.parse()

    def post(self, value):
        assert self.endpoint != None
        if self.resource:
            self.r = requests.post(self.url(), data=value)
        elif value is None:
            self.r = requests.post(self.url(), json=self.barams)
        else:
            raise Exception("[POST] Unusable value: " + value)
        return self.parse()

    def delete(self, value):
        assert self.endpoint != None
        self.r = requests.delete(self.url(), data=value)
        return self.parse()

    def url(self):
        pr = self.base_url + self.endpoint
        if len(self.params) > 0:
            pr += '?'
            pr += '&'.join([str(k) + '=' + str(v) for k, v in self.params.items()])
        return pr


