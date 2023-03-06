import json

file = open('medicina_galego_resultado.json', 'r')

dic = json.load(file)
file.close()
new_dic = []

for key,entry in dic['completas'].items():
    try:
      aux = {
          'termo_universal' : entry['traducoes']['en'][0],
          'areas' : entry['areas'],
      }
      traducoes = {}
      for key,lang in entry['traducoes'].items():
          if len(lang) > 0:
            traducoes[key] = {
                'termo' : lang[0]
            }
            if len(lang) > 1:
              traducoes[key]['sin'] = lang[1:]  
      traducoes['ga'] = {
          'termo' : entry['nome']
      }
      sin = [x for x in entry['sinonimos'] if x != '']
      var = [x for x in entry['variacoes'] if x != '']
      if len(sin)>0:
        traducoes['ga']['sinonimos'] = sin
      if len(var)>0:
        traducoes['ga']['variacoes'] = var
      if entry['nota']:
        traducoes['ga']['nota'] = entry['nota']
      aux['traducoes'] = traducoes
      new_dic.append(aux)
    except :
       print("*"*10)
       print(f'Error on entry: {entry}')
       print("*"*10)

new_dic = sorted(new_dic, key=lambda x:x['termo_universal'])


text = json.dumps(new_dic,indent=4)

file = open('global_medicina_resultado.json', 'w')
file.write(text)
file.close()

file = open('dicionario_global_medicina.txt','w')

for entry in new_dic:
    try:
      file.write(f'Area: ')
      ult=''
      if len(entry['areas']) > 0:
        for area in entry['areas'][:-1]:
          file.write(f'{area};')
        ult = entry['areas'][-1]
      file.write(f'{ult}\n')
      for ln in entry['traducoes']:
        file.write(f'{ln[0].upper()}{ln[1]}:\n')
        traducoes = entry['traducoes'][ln]
        termo = traducoes['termo']
        file.write(f'-{termo}\n')
        if 'sinonimos' in traducoes:
          for sinonimo in traducoes['sinonimos']:
            file.write(f'-{sinonimo}\n')
        if 'variacoes' in traducoes:
          for variacao in traducoes['variacoes']:
            file.write(f'+var: {variacao}\n')
      file.write('\n')
    except :
      print(entry)
      break

file.close()