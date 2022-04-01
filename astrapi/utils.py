class MoldException(Exception):
    pass

def catching(fun, getkey):
    def __catching_method__(*args, **kwargs):
        try:
            res = fun(*args, **kwargs)
        except Exception as e:
            raise Exception(str(e) + ' ]--> catching on ' + getkey(*args, **kwargs))
        return res
    return __catching_method__

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return repr(self.__dict__)
    def __iter__(self):
        return ( _ for _ in self.__dict__.keys())
    def identify(self):
        if hasattr(self, '__name__'):
            return self.__name__
        else:
            return repr(self.__dict__.keys())
    def mold(self, *args, **kwargs):
        data = {}
        for key in self:
            try:
                data[key] = getattr(self, key)(*args, **kwargs)
            except Exception as e:
                raise MoldException("[" + self.identify() + "] > Molding error working on key '" + key +\
                                    "' ==> " + str(e))
        return data

def schematize(schematics, keys, **kwargs):
    def __schema_generator__():
        for key in keys:
            schema = Namespace(**{
                attr_name: fun(key) for attr_name, fun in schematics.items()
            })
            yield key, schema
    return __schema_generator__

def organize(generator):
    return {
        key: value for key, value in generator()
    }

def populate(schema, method, *args, **kwargs):
    #method = catching(method, lambda *args, **kwargs: args[0])
    return {
        key: method(key, value, *args, **kwargs) for key, value in schema.items()
    }

def suffix(s):
    def __suffix_applicator__(fun):
        fun.__name__ += s
        return fun
    return __suffix_applicator__

flatten = lambda l: [item for sublist in l for item in sublist]
dict_flatten_values = lambda d: [item for v in d.values() for item in v]

def dikwarg(**kwargs):
    return kwargs