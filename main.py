#              ▓███                  
#            ░█████                  Привет брат, я рад что ты зашёл сюда, данный код был сделан на коленке под двумя
#            ██████                  банками хмельного, пусть и так, но ты же этим заинтересовался, и я очень благодарен тебе! )
#            ██████                  
#            ▒█████                  Контакт для связи и предложений: Telegram @lisurgut.
#             ▒████                  
#                ░░█▓░               Если используешь информацию из данного кода, будь добр - не выставляй за лично своё,
#                  █████░            буду рад если укажешь моё соавторство или хотя бы где то сможешь упомянуть меня как разработчика <3
#                  █████▓            
#                  ██████            ██ █ ███████ ██ █ ██ █████ █ ██████ ██████ █ █████ █ █ ████████ █ ███ █ ██ ██ █████ █ █ ████████ ██
#                  █████▓            █ █ ███ █ █████ ██ ███ █ ███████ ███ █████ █ █████ ██ ███████ ████ █ ██ █ █ █ ████ █ ███ █████ ██ █
#                  █████░            █ █████ ███ ███████ ██ ███ █ █████ █████ ███ █ █████ █ ██ █████ ██████ ██ ███ ████ ███ ███ ██████ █
#                  ██▓░               







import configparser,asyncio,sys,requests,re,io,urllib.parse,json,os,time
from telethon import TelegramClient,functions,types,errors,events,utils
from telethon.extensions import html
from PIL import Image, ImageDraw
from yandex_music import Client as YMClient

c=configparser.ConfigParser();c.read('config.ini',encoding='utf-8')
try:
 AID,AHS=c.getint('telegram','api_id'),c.get('telegram','api_hash')
 CID,MID=c.getint('telegram','cid'),c.getint('telegram','mid')
 PACK,LKY,LUS=c.get('telegram','pack_name'),c.get('lastfm','api_key'),c.get('lastfm','username')
 YTOK=c.get('yandex','token',fallback=None)
 if not all([AID,AHS,CID,MID,LKY,LUS,PACK]):raise ValueError
except:sys.exit("❌ CONFIG ERROR: Проверьте config.ini")

cl=TelegramClient('session',AID,AHS);ym=YMClient(token=YTOK) if YTOK else YMClient()
mem={'trk':None,'lnk':{},'cv_id':None,'last_msg':'','stop_ticks':0}
CV='covers_cache.json';cv_c=json.load(open(CV,encoding='utf-8')) if os.path.exists(CV) else {}
def sv():json.dump(cv_c,open(CV,'w',encoding='utf-8'),ensure_ascii=False)
def lg(t,m):print(f"[{time.strftime('%H:%M:%S')}] {t} {m}")
def u16(s):return len(s.encode('utf-16-le'))//2

def parse_hybrid(txt):
 t,ents=html.parse(txt);ms=list(re.finditer(r'\{emoji=(\d+)\}',t))
 for m in reversed(ms):
  s,e=m.span();eid=int(m.group(1));rep="👾"
  s16=u16(t[:s]);l_old=u16(t[s:e]);l_new=u16(rep);dt=l_new-l_old
  t=t[:s]+rep+t[e:]
  for en in ents:
   if en.offset>=s16+l_old:en.offset+=dt
   elif en.offset+en.length>=s16+l_old:en.length+=dt
  ents.append(types.MessageEntityCustomEmoji(s16,l_new,eid))
 return t,ents

@cl.on(events.NewMessage(outgoing=True,pattern=r'\.test'))
async def tst(e):
 await e.edit("🔄 <b>Check...</b>",parse_mode='html')
 try:
  s=await cl(functions.messages.GetStickerSetRequest(types.InputStickerSetShortName(PACK),0))
  if not s.documents:await e.edit(f"❌ Empty: {PACK}");return
  m=f"📦 <a href='https://t.me/addemoji/{PACK}'>{PACK}</a>\n"
  for d in s.documents[-3:]:m+=f"🆔 <code>{d.id}</code>: {{emoji={d.id}}}\n"
  t,en=parse_hybrid(m)
  await e.edit(t,formatting_entities=en,link_preview=True)
 except Exception as x:await e.edit(f"Err: {x}")

def g_trk():
 try:
  r=requests.get(f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={LUS}&api_key={LKY}&format=json&limit=1",timeout=2).json()
  t=r['recenttracks']['track'][0];i=t['image'][-1]['#text'] if t['image'] else None
  if i=='':i=None
  # Если нет атрибута nowplaying -> трек на паузе/история
  playing = t.get('@attr',{}).get('nowplaying')=='true'
  return {'play':playing,'art':t['artist']['#text'],'tit':t['name'],'img':i}
 except:return None

def g_itu(q):
 try:
  r=requests.get(f"https://itunes.apple.com/search?term={urllib.parse.quote(q)}&entity=song&limit=1",timeout=2).json()
  if r['resultCount']>0:return r['results'][0]['artworkUrl100'].replace('100x100','600x600')
 except:pass;return None

def g_yam(q):
 try:
  s=ym.search(q);
  if s.best and s.best.type=='track':return "https://" + s.best.result.cover_uri.replace('%%','400x400')
 except:pass;return None

def f_lnk(a,t):
 q=f"{a} {t}";d={};lg("SRC",q)
 try:
  r=requests.get(f"https://api.song.link/v1-alpha.1/links?userCountry=RU&songIfNoneFound=true&q={urllib.parse.quote(q)}",timeout=3,headers={'User-Agent':'Mozilla/5.0'}).json()
  for k,v in r.get('linksByPlatform',{}).items():d[k]=v['url']
 except:pass
 if 'yandex' not in d:
  try:
   s=ym.search(q)
   if s.best and s.best.type=='track':tr=s.best.result;d['yandex']=f"https://music.yandex.ru/album/{tr.albums[0].id}/track/{tr.id}";lg("YAM",f"ID: {tr.id}")
  except:pass
 return d

async def up_cv(u,k):
 if k in cv_c:return cv_c[k]
 lg("CV",f"Load: {u[:30]}...");b=io.BytesIO()
 try:
  i=Image.open(io.BytesIO(requests.get(u).content)).convert('RGBA').resize((100,100),Image.Resampling.LANCZOS)
  msk=Image.new('L',(100,100),0);ImageDraw.Draw(msk).rounded_rectangle((0,0,100,100),radius=25,fill=255)
  i.putalpha(msk);i.save(b,'PNG');b.seek(0);b.name="c.png"
  tm=await cl.send_file('me',b,force_document=True,attributes=[types.DocumentAttributeFilename('c.png')])
  di=utils.get_input_document(tm.media.document)
  try:
   s=await cl(functions.messages.GetStickerSetRequest(types.InputStickerSetShortName(PACK),0))
   if len(s.documents)>=50:
    td=s.documents[0];await cl(functions.stickers.RemoveStickerFromSetRequest(types.InputDocument(td.id,td.access_hash,td.file_reference)))
  except errors.StickersetInvalidError:lg("ERR","Pack 404");await tm.delete();return None
  await cl(functions.stickers.AddStickerToSetRequest(types.InputStickerSetShortName(PACK),types.InputStickerSetItem(di,'💿',keywords='c')))
  await tm.delete();await asyncio.sleep(1)
  s=await cl(functions.messages.GetStickerSetRequest(types.InputStickerSetShortName(PACK),0))
  nid=s.documents[-1].id;cv_c[k]=nid;sv();lg("OK",f"ID: {nid}");return nid
 except Exception as e:lg("ERR",e);return None

async def main():
 try:await cl.start()
 except:sys.exit("❌ Auth")
 lg("BOT","Ready");lv=None
 while 1:
  try:
   c=g_trk()
   if c and c['play']:mem['stop_ticks']=0;lv=c
   else:
    mem['stop_ticks']+=1;c=lv if mem['stop_ticks']<5 and lv else None
   
   tx=""
   if c:
    fn=f"{c['art']} - {c['tit']}"
    if mem['trk']!=fn:
     lg("NP",fn);mem['trk']=fn;im=c['img']
     if not im:im=g_itu(fn)
     if not im:im=g_yam(fn)
     if im:mem['cv_id']=await up_cv(im,fn)
     else:lg("WARN","No cover found");mem['cv_id']=None
     mem['lnk']=f_lnk(c['art'],c['tit'])
    
    tx=config_get('true_mes').replace('{name}',c['art']).replace('{title}',c['tit'])
    if '{cover}' in tx:tx=tx.replace('{cover}',f"{{emoji={mem['cv_id']}}}" if mem['cv_id'] else "")
    for s in re.findall(r'\{link_to=(.*?)\}',tx):
     k='yandex' if 'yandex' in s else 'spotify' if 'spotify' in s else 'soundcloud' if 'soundcloud' in s else 'appleMusic' if 'apple' in s else 'youtube' if 'youtube' in s else s
     tx=tx.replace(f'{{link_to={s}}}',mem['lnk'].get(k,"#"))
   else:
    tx=config_get('false_mes');mem['trk']=None
   
   f_txt,ents=parse_hybrid(tx.strip())
   
   if f_txt!=mem['last_msg']:
    try:await cl.edit_message(CID,MID,text=f_txt,formatting_entities=ents,link_preview=False);mem['last_msg']=f_txt;lg("UP","Updated")
    except errors.MessageNotModifiedError:mem['last_msg']=f_txt
    except errors.FloodWaitError as e:await asyncio.sleep(e.seconds)
  except Exception as e:lg("ERR",e)
  await asyncio.sleep(1.2)

def config_get(k):return c.get('telegram',k,raw=True).replace('\\n','\n')

with cl:cl.loop.run_until_complete(main())


#              ▓███                  
#            ░█████                  Привет брат, я рад что ты зашёл сюда, данный код был сделан на коленке под двумя
#            ██████                  банками хмельного, пусть и так, но ты же этим заинтересовался, и я очень благодарен тебе! )
#            ██████                  
#            ▒█████                  Контакт для связи и предложений: Telegram @lisurgut.
#             ▒████                  
#                ░░█▓░               Если используешь информацию из данного кода, будь добр - не выставляй за лично своё,
#                  █████░            буду рад если укажешь моё соавторство или хотя бы где то сможешь упомянуть меня как разработчика <3
#                  █████▓            
#                  ██████            ██ █ ███████ ██ █ ██ █████ █ ██████ ██████ █ █████ █ █ ████████ █ ███ █ ██ ██ █████ █ █ ████████ ██
#                  █████▓            █ █ ███ █ █████ ██ ███ █ ███████ ███ █████ █ █████ ██ ███████ ████ █ ██ █ █ █ ████ █ ███ █████ ██ █
#                  █████░            █ █████ ███ ███████ ██ ███ █ █████ █████ ███ █ █████ █ ██ █████ ██████ ██ ███ ████ ███ ███ ██████ █
#                  ██▓░               