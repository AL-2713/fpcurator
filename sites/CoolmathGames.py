# Coolmath Games definition. Only supports HTML5 because all flash games are already curated except those on wayback.
# Some games can only be curated through https links.

import fpclib
import json, bs4, re, zipfile
import datetime

regex = 'coolmath-?games.com'
ver = 6

HTML_FILES = re.compile(r'.*\.(js|html|css|json)$')

class CoolmathGames(fpclib.Curation):
    def parse(self, soup):
        # Get Title
        title = json.loads(str(soup.findAll('script', type='deferjs')[3]).split('gameDefData = ')[1].split(';')[0])[0]['title']

        cmd_file = self.get_meta('url')
        if cmd_file.endswith('/'):
            cmd_file += 'index.html'
        else:
            cmd_file += '/index.html'
        # Get Launch Command
        cmd = fpclib.normalize(cmd_file)
        
        # Get Description
        try:
            desc = soup.find('meta', attrs={"name":"description"})['content'].replace('  ', '\n')
        except:
            desc = ""

        try:
            for elem in soup.find('div', class_='game-instructions').children:
                if isinstance(elem, bs4.NavigableString):
                    continue
                for part in elem.children:
                    desc += '\n\n' + part.text
        except:
            pass

        # Get embed url
        play_file = cmd_file.replace('/index.html', '/play.html')
        play_soup = fpclib.get_soup(play_file[:-5])
        try:
            base_elem = play_soup.find('base')['href'][2:]
        except:
            base_elem = 'www.coolmathgames.com' + play_soup.find('iframe1')['src'].split('?')[0]
            
        
        self.set_meta(base_elem=base_elem)
        
        
        drupal = soup.find('script', attrs={'data-drupal-selector': 'drupal-settings-json'}).contents[0]
        embed = json.loads(drupal)['cmatgame']['html5embed']
        if embed:
            html_embed = '<iframe src="http://%s" width="100%%" height="100%%" scrolling="no" marginwidth="0" vspace="0" frameborder="0" hspace="0" marginheight="0"></iframe>' % (base_elem)
            self.set_meta(zip_file='https://www.coolmathgames.com/' + embed['game']['u'])
        else:
            fpclib.debug("Coolmath Games zip not found. Game may not launch properly.", 1, pre="[WARN] ")
            html_embed = '<iframe src="http://%s" width="%spx" height="%spx" scrolling="no" marginwidth="0" vspace="0" frameborder="0" hspace="0" marginheight="0"></iframe>' % (base_elem, '100%', '100%')

        style = 'body { background-color: #16202c; height: 100%; margin: 0; }\n            iframe { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }'
        html = '<html>\n    <head>\n        <title>%s</title>\n        <style>\n            %s\n        </style>\n    </head>\n    <body>\n        %s\n    </body>\n</html>' % (title, style, html_embed)
        
        date = soup.findAll('div',class_="field-row-right")[3].text.strip()
        newDate = datetime.datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
        
        # Set meta
        self.set_meta(
            html=html,
            play_file=play_file,
            title=title,
            pub='Coolmath Games',
            tech='HTML5',
            date=newDate,
            app=fpclib.FPNAVIGATOR,
            cmd_file=cmd_file,
            cmd=cmd,
            desc=desc
        )

        # Get Screenshot (Site screenshots should not be used)
        #try:
            #self.ss = soup.find('meta', property='og:image')['content']
        #except:
            #pass

    def get_files(self):
        cmd_file = self.get_meta('cmd_file')
        zip_file = self.get_meta('zip_file')
        play_file = self.get_meta('play_file')
        base_elem = self.get_meta('base_elem')

        # Write embed
        fpclib.write(cmd_file[cmd_file.index('://')+3:], self.get_meta('html'))
        
        # Download zipped assets   
        if zip_file:
            file_base = base_elem
            fpclib.make_dir(file_base)
            fpclib.download(zip_file)
            local_zip = zip_file[zip_file.rfind('/')+1:]
            with zipfile.ZipFile(local_zip, 'r') as zip_ref:
                zip_ref.extractall(file_base)
            fpclib.delete(local_zip)

        # Replace references to https in all content files
        fpclib.replace(fpclib.scan_dir('', HTML_FILES)[0], 'https:', 'http:')
        
        
