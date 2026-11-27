import urllib.request, hashlib, io, zipfile, xml.etree.ElementTree as E, datetime as dt, collections as C, bisect, decimal as D, json
url='https://archive.ics.uci.edu/static/public/352/online+retail.zip'
with urllib.request.urlopen(url,timeout=35) as f: raw=f.read(65000000)
assert hashlib.sha256(raw).hexdigest() == 'f5385cbb54bbebf7196389109c6b0621faab0c304e3702548165e71c84aede8b'
z=zipfile.ZipFile(io.BytesIO(raw)); name=next(n for n in z.namelist() if n.endswith('.xlsx')); book=zipfile.ZipFile(io.BytesIO(z.read(name))); k='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
strings=[''.join(n.text or '' for n in s.iter(k+'t')) for s in E.fromstring(book.read('xl/sharedStrings.xml'))]
root=None; positives=C.defaultdict(list); credits=[]; total=0; stages=C.Counter(); excluded_invoices=set()
for event,row in E.iterparse(book.open('xl/worksheets/sheet1.xml'),events=('start','end')):
 if event=='start' and row.tag==k+'sheetData': root=row
 if event!='end' or row.tag!=k+'row':continue
 if row.get('r')=='1':print('HEADER',[strings[int(c.findtext(k+'v'))] for c in row if c.get('t')=='s'],flush=True);root.remove(row);continue
 total+=1; vals={}
 for c in row:
  v=c.findtext(k+'v'); col=c.attrib['r'][0]
  if v is not None: vals[col]=strings[int(v)] if c.get('t')=='s' else v
 root.remove(row)
 inv=vals.get('A',''); credit=inv.upper().startswith('C')
 if credit:stages['cancel_rows']+=1
 if not all(a in vals for a in 'ABDEFG'):
  if credit:stages['cancel_missing_identifiers']+=1; excluded_invoices.add(inv)
  continue
 q=int(vals['D']); epoch=round(float(vals['E'])*1440); price=D.Decimal(vals['F']); sku=vals['B'].strip().upper()
 if not sku[:1].isdigit() or price<=0 or (q>=0 if credit else q<=0):
  if credit:stages['cancel_excluded_non_product_or_sign_or_price']+=1; excluded_invoices.add(inv)
  continue
 key=(vals['G'],sku,abs(q),price)
 if credit: credits.append((epoch,inv,key))
 else: positives[key].append((epoch,inv))
for hits in positives.values():hits.sort()
first=(dt.date(2011,3,1)-dt.date(1899,12,30)).days*1440
cases=sorted(set((minute,inv,key) for minute,inv,key in credits if minute>=first))
groups=C.defaultdict(list)
for minute,inv,key in cases:groups[inv].append((minute,key))
def candidates(minute,key,window,loose):
 hits=(no_qty if loose else positives).get((key[0],key[1],key[3]) if loose else key,[])
 a=bisect.bisect_left(hits,(minute-window*1440,'')); b=bisect.bisect_left(hits,(minute,''))
 return {inv for _,inv in hits[a:b]}
no_qty=C.defaultdict(list)
for (customer,sku,qty,price),hits in positives.items():no_qty[customer,sku,price].extend(hits)
for hits in no_qty.values():hits.sort()
def classify(rows,window,loose):
 sets=[candidates(m,k,window,loose) for m,k in rows]
 return min(len(set.intersection(*sets)),2)
assert len(groups)==2656 and len(cases)==6764 and total==541909
result={}; monthly=C.defaultdict(C.Counter)
for loose in (False,True):
 for sample in ('eligible','all_rows_covered'):
  counts=C.Counter(); multi=C.Counter()
  for inv,rows in groups.items():
   if sample=='all_rows_covered' and inv in excluded_invoices:continue
   a=classify(rows,30,loose); b=classify(rows,90,loose)
   assert a<=b
   tag=f'{a}->{b}';counts[tag]+=1
   if len(rows)>1:multi[tag]+=1
   if not loose and sample=='all_rows_covered':
    month=(dt.datetime(1899,12,30)+dt.timedelta(minutes=min(m for m,_ in rows))).strftime('%Y-%m'); monthly[month][tag]+=1
  result[f'{sample}/'+('drop_quantity' if loose else 'strict')]={'n':sum(counts.values()),'transitions':dict(counts),'multi_line_transitions':dict(multi)}
print(json.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'groups':result,'monthly':monthly},sort_keys=True),flush=True)

def test_transition_counts():
    expected = {'0->0': 2096, '0->1': 81, '0->2': 7, '1->1': 376, '1->2': 27, '2->2': 21}
    assert result['all_rows_covered/strict']['transitions'] == expected
    assert result['all_rows_covered/drop_quantity']['transitions'] == {'0->0': 617, '0->1': 214, '0->2': 25, '1->1': 1472, '1->2': 170, '2->2': 110}
    assert sum(expected.values()) == 2608
    assert expected['0->0'] + expected['0->1'] + expected['0->2'] == 2184

test_transition_counts()
