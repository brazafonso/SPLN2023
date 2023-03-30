import pickle



file = open('entries_dic','rb')

dic = pickle.load(file)
file.close()

pagHTML = '''
<!DOCTYPE html>
  <html>
    <head>
      <meta charset="UTF-8" />
      <title>Medicine dictionary</title>
      <link rel="stylesheet" href="w3.css">
    </head>
    <body>
      <div class="w3-card-4">
        <header class="w3-container w3-blue">
        <h1>Medicine dictionary</h1>
        </header>
      </div>

        <div class="w3-container w3-border w3-border-light-blue">
        <table>
          <tr>
            <td width="30%" valign="top">
              <a name='indice'>
              <h2>Índice</h2>
              <ul>
'''
termos = []
entries = []
for entry in dic:
    for termo in entry['languages']['Ga'].keys():
      termos.append(termo)

      e = {'languages':{},'atributes':{}}
      for language,value in entry['languages'].items():
        e['languages'][language] = value
      for atribute,value in entry['atributes'].items():
        e['atributes'][atribute] = value
      entries.append((termo,e))
      break

termos = sorted(termos,key=lambda x:x)
entries = sorted(entries,key=lambda x:x[0])

for termo in termos:
    pagHTML += f'''
                <li>
                  <a href="#{termo.replace(' ','')}">{termo}</a>
                </li>
    '''

pagHTML += '''
              </ul>
          </td>
          <td width="70%">
'''

for entry in entries:
    pagHTML += f'''
                <div>
                  <a name="{entry[0].replace(' ','')}"/>
                  <h3>{entry[0]}</h3>
                  <table class="w3-table-all" width="100%">
                    <tr  width="100%">
                      <th width="50%"><h4>Atributes</h4></th><th width="50%"><h4>Translations</h4></th>
                    </tr>
                    <tr width="100%">
                      <td width="50%">

    '''
    for key,atribute in entry[1]['atributes'].items():
      pagHTML +=f'''
                      <h5><b>{key}</b></h5>
      '''
      for name in atribute.keys():
         pagHTML +=f'''
                      <center><h6>{name}</h6></center>
        '''

    pagHTML += '''
                      </td>
                      <td width="50%">
    '''

    for ln,atribute in entry[1]['languages'].items():
      pagHTML +=f'''
                      <h5><b>{ln}</b></h5>
      '''
      for translation in atribute.keys():
         pagHTML +=f'''
                      <center><h6>{translation}</h6></center>
        '''
       
    pagHTML +='''
                      </td>
                    </tr>
                  </table>
                  <address>[<a href="#indice"> Voltar ao índice </a>]</address>
                </div>
                <center>
                  <hr width="100%"/>
                </center>
    '''




pagHTML += '''
            </td>
          </tr>
        </div>
        </table>
      </div>

        <footer class="w3-container w3-blue w3-bottom">
          <h5>Generated in SPLN2023-TPC3</h5>
        </footer>
      </div>
    </body>
  </html>
'''


file = open("dicionario.html",'w')

file.write(pagHTML)
file.close()