from .database import getSpreadSheetDatabase, database_schema, gspread, client
import time

def filter_cols(cols, value):
    return (idx for idx, val in enumerate(cols) if val == value)

def _query_rows(ws, keys):
    i = 1
    rows = None
    for key, value in keys.items():
        cs = ws.col_values(i)
        ids = filter_cols(cs, value)
        if rows is None:
            rows = ids
        else:
            rows = set(rows).intersection(ids)
        i += 1
    return i, rows

def _verify_row(ws, cell, keys):
    row = cell.row
    for idx, value in enumerate(keys.values()):
        c = ws.cell(row, idx + 1)
        if c.value != value:
            return False
    return True

class OptimizeSheet:
    def __init__(self, table, **kwargs):
        self.table = table

class DBInterface:
    def __init__(self):
        self.sh = getSpreadSheetDatabase()
        self.optimize = False

    def __getattr__(self, name):
        if name in ['get', 'set', 'delete']:
            if self.optimize:
                assert name == 'get', (name, self.optimize)
                return getattr(self, '_' + name + '_optimize')
            else:
                return getattr(self, '_' + name)

    def _assert(self, table, _pass=False, **keys):
        _keys = database_schema[table]
        ps = keys.keys()
        assert not 'txt' in ps
        if not _pass:
            for key in _keys:
                if key != 'txt':
                    assert key in ps, (table, key, ps)
        try:
            ws = self.sh.worksheet(table)
        except gspread.exceptions.APIError as e:
            print (e.args)
            if "UNAUTHENTICATED" in str(e):
                client.login()
                return self._assert(table, **keys)
            elif "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(30)
                return self._assert(table, _pass=_pass, **keys)
            else:
                raise e
        if not _pass:
            assert ws.row_values(1) == _keys, str(ws.row_values(1)) + str(_keys)
        return ws

    def _get(self, table, **keys):
        ws = self._assert(table, **keys)
        i, rows = _query_rows(ws, keys)
        return [ws.cell(idx + 1, i).value for idx in rows]

    def _set(self, table, value, **keys):
        ws = self._assert(table, **keys)
        try:
            ws.find(value)
        except gspread.exceptions.CellNotFound:
            pass
        else:
            return False
        values = list(keys.values())
        #print (values)
        values.append(value)
        ws.insert_row(values, 2)
        return True

    def _delete(self, table, value, **keys):
        ws = self._assert(table, **keys)
        res = False
        try:
            cells = ws.findall(value)
        except gspread.exceptions.CellNotFound:
            raise Exception('Value already exists.')
        else:
            for cell in cells:
                #print (cell)
                if _verify_row(ws, cell, keys):
                    ws.delete_row(cell.row)
                    res = True
        return res

    # Opti
    def _get_optimize(self, table, **keys):
        try:
            ws, records = self.data[table]
            results = []
            for rec in records:
                stop = False
                for k,v in keys.items():
                    if rec[k] != v:
                        #if k == 'ruler':
                        #    print ("STOP BECAUSE OF: ", k, v, '!=', rec[k], rec.keys())
                        stop = True
                        break
                if stop:
                    continue
                #print ("FOUND: ", k, v, rec[k])
                results.append(rec['txt'])
            return results
        except Exception as ex:
            print (ex)
            raise ex
        #ws = self._assert(table, **keys)
        #i, rows = _query_rows(ws, keys)
        #return [ws.cell(idx + 1, i).value for idx in rows]

    def _set_optimize(self, table, value, **keys):
        raise Exception('NotImplemented')

    def _delete_optimize(self, table, value, **keys):
        raise Exception('NotImplemented')

    # Context
    def loads(self, *args):
        assert self.optimize is True
        for arg in args:
            ws = self._assert(arg, _pass=True)
            self.data[arg] = (ws, ws.get_all_records())
    def __enter__(self):
        self.optimize = True
        self.data = {}
        return self
    def __exit__(self, et, ev, tb):
        #print (self.data)
        self.optimize = False

if __name__ == "__main__":
    db = DBInterface()
    db.set('planet_sign_txts', "This is my interpretation.", planet="jupiter", sign="libra")
    db.delete('planet_sign_txts', "This is my interpretation.", planet="jupiter", sign="libra")
    li = db.get('planet_sign_txts', planet="jupiter", sign="libra")
    print (li)