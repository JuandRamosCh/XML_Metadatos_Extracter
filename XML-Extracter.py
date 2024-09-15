#pip install unidecode


import xml.etree.cElementTree as et #se importa el paquete que permite trabajar con xml
import re  #se importa el paquete para reemplazar partes de strings
import os  #se importa la librería os para trabajar con archivos
from unidecode import unidecode #se importa librería para estandarizar texto



directory = "Tu_carpeta_input"
directory = directory.replace("\\", "/")
OutFold = "Tu_carpeta_output" 
OutFold = OutFold.replace("\\", "/")




def mDatos(filepath):   #definición de la función para extraer metadatos de un xml, poniendo la ruta del archivo

    tree=et.parse(filepath)     #se sacan los datos del xml
    root=tree.getroot()
    


    function = "full text"                                                                      #Se define que irá en función
    journal = "Revista Internacional de Gestion del Conocimiento y la Tecnologia (GECONTEC)"    #Se define el nombre de la journal                  
    classification = "M1, M15, O3, O31, O32, D8, D81"                                           #Se define las clasificaciones
    template = "ReDIF-Article 1.0"                                                              #Se dfine el template


    agregM = ""


    #Encontrar el index de artículos dentro del xml
    for i in range(len(root)):
        if ("articles" in root[i].tag):
            ArtsInd = i
        
        
    #Encontrar el index de identificación de issue dentro del xml
    for i in range(len(root)):
        if ("issue_identification" in root[i].tag):
            idIssue = i       
    
    #Encontrar el index de publicación dentro de los artículos
    for j in range(len(root[ArtsInd])):
        for child in range(len(root[ArtsInd][j])):
            if ("publication" in root[ArtsInd][j][child].tag):
                publi = child


    #Encontrar el index de autores dentro de los artículos
        for child in range(len(root[ArtsInd][j][publi])):
            if ("authors" in root[ArtsInd][j][publi][child].tag):
                auths = child
   

    #Datos de publication
        #sacar abstract
        listabstract = []
        for child in root[ArtsInd][j][publi]:                       #pone todos los abstracts en una lista
            if "abstract" in child.tag:
                listabstract.append("Abstract: "+child.text[3:-4])
        
        try:        
            abstract = listabstract[-1]                                 #si hay uno agarra el único, sino agarra el útlimo que es el que está en español (idioma original)
            abstract = re.sub(r'<[^>]*>', '', abstract)                 #Quita notaciones tipo "<texto>" que se usan para poner texto en negrita, cursiva o subrayado
            abstract = unidecode(abstract)                              #se estandariza el texto
        except IndexError:
            abstract = "Abstract: "
            
        #sacar title
        listTitle = []
        for child in root[ArtsInd][j][publi]:                       #pone los títulos en una lista
            if "title" in child.tag:
                listTitle.append("Title: "+child.text+"\n")
        if len(listTitle) == 1:
            title = listTitle[0]                                    #si hay un solo título, toma ese
        else:
            title = f"{listTitle[1][:-1]}({listTitle[0][7:-1]})"    #si hay título en el idioma original y en ingles, se pone el original y luego el de inglés entre paréntesis
            
        
        title = unidecode(title)                                    #se estandariza el título
    

        #sacar las páginas que hay en un artículo
        for child in root[ArtsInd][j][publi]:
            if "pages" in child.tag:
                pages = child.text


        #sacar url (zeonodo) de cada artículo
        list1=[]
        for child in root[ArtsInd][j][publi]:
            if "id" in child.tag:
                list1.append(child.text)
        url = list1[-1]
        

    #Datos de issue identification
        #sacar volumen del issue
        for child in root[idIssue]:
            if "volume" in child.tag:
                volume = child.text


        #sacar issue
        for child in root[idIssue]:
            if "number" in child.tag:
                issue = child.text


        
    #Sacar datos de los autores
        listNoms = []       #se define una lista donde se guardarán datos de nombres
        
        for i in range(len(root[ArtsInd][j][publi][auths])):
            listNames = []                                      #se define una lista donde se guardarán los nombres
            listMail = []                                       #se define una lista donde se guardarán los correos
            listWork = []                                       #se define una lista donde se guardarán los lugares de trabajo
            for c in root[ArtsInd][j][publi][auths][i]:
                if "mail" in c.tag:                                 
                    listMail.append("Author-Email: "+c.text)      #si el correo es el correcto, se añade a su lista
                if "name" in c.tag:
                    listNames.append(c.text)                          #se añade el nombre a su lista
                if "affiliation" in c.tag:
                    listWork.append("Author-Workplace-Name: "+c.text) #se añade el lugar de trabajo a su lista
            listNamesFin = []
            listNamesFin.append("Author-Name: "+ listNames[0]+" " +listNames[1] ) #Se juntan los nombres y apellidos en una lista
            listNoms = listNoms + listNamesFin + listMail + listWork              #Se ponen todos los datos en una sola lista
            
                
                
        nombre = '\n'.join(listNoms)        #se pone la lista de todos los datos como un string con los datos separados por un salto de línea
        nombre = unidecode(nombre)          #se estandarizan los nombres
                    

        
    
        #sacar formato del archivo       
        for child in range(len(root[ArtsInd][j])):
            if "submission_file" in root[ArtsInd][j][child].tag:
                for i in range(len(root[ArtsInd][j][child])):
                    if "name" in root[ArtsInd][j][child][i].tag:
                        if root[ArtsInd][j][child][i].text[-4:-3] == ".":
                            formato = root[ArtsInd][j][child][i].text[-3:]
                
           
        #sacar fecha del artículo (si no tiene fecha, se saca la del volumen)
        try:
            for child in root[ArtsInd][j]:
                if "publication" in child.tag:
                    año = child.attrib["date_published"][:4]   #año
                    mes = child.attrib["date_published"][5:7]  #mes  
        except Exception:
            for child in root:
                if "date_published" in child.tag:
                    año = child.text[0:3]
                    mes = child.text[5:7]
                    
                
 

        # sacar keywords 
        listkeywords = [] 
        for i in range(len(root[ArtsInd][j][publi])):                               #Saca las keywords y las pone en una lista
            if "keywords" in root[ArtsInd][j][publi][i].tag:
                for r in range(len(root[ArtsInd][j][publi][i])):
                    listkeywords.append(root[ArtsInd][j][publi][i][r].text+", ")
        if len(listkeywords) != 1:                                                  #si hay más de una keyword, convierte la lista en string y saca el espacio y comas al final
            keywords = "".join(listkeywords) 
            keywords = keywords[:-2]
        else:
            keywords = listkeywords[0]                                              #si hay una keyword, solo extrae esa
          
        keywords = unidecode(keywords)                                              #se estandarizan las keywords
 
        #se establece el handle con los datos extraídos        
        handle = "RePEc:rge:journl:"+"v:" + volume +":y:"+ año +":i:"+issue+":p:"+pages
            
        
        #Se ponen todos los metadatos extraídos en una lista
        
        if len(url)>5:
            metadatos = [f"Template-Type: {template}",
                         nombre,title,abstract,f"Classification-JEL: {classification}",
                         f"Keywords: {keywords}",f"Journal: {journal}","Pages: "+pages,f"Volume: {volume}", f"Issue: {issue}",f"Year:{año}",f"Month: {mes}",
                         f"File-URL: https://doi.org/{url}",f"File-Format: Application/{formato}",f"File-Function: {function}",f"Handle: {handle}"]
        else:
            metadatos = [f"Template-Type: {template}",
                         nombre,title,abstract,f"Classification-JEL: {classification}",
                         f"Keywords: {keywords}",f"Journal: {journal}","Pages: "+pages,f"Volume: {volume}", f"Issue: {issue}",f"Year:{año}",f"Month: {mes}",
                         "File-URL: ",f"File-Format: Application/{formato}",f"File-Function: {function}",f"Handle: {handle}"]
        
        #está sin número
        metadatosSTR = '\n'.join(metadatos)   #Poner los metadatos en un string y separarlos por líneas
        metadatosSTR = metadatosSTR + '\n'   #separa los artículos con una linea "_______" al final
        agregM = agregM + metadatosSTR
        

        
    return agregM     #la función regresa los metadatos del artículo



file_list = os.listdir(directory)  #Crea una lista con los archivos de la carpeta



#Se itera la función por cada archivo de la carpeta en orden
listAcum=[]
for filename in file_list:
    filepath = os.path.join(directory, str(filename))
    if os.path.isfile(filepath):  
        var = mDatos(filepath)
    listAcum.append(var)
    
    
#se pone los metadatos de cada volumen en la carpeta seleccionada     
#for i in range(len(listAcum)):
#    final = listAcum[i] + "\n"   
#    f = open(f"{OutFold}/datos{i}.rdf","w",encoding="utf-8")   
#    f.write(final)
#    f.close()
    
    
acumTodo = ""

for i in listAcum:
    acumTodo += i
    
    
f = open(f"{OutFold}/Papers.rdf","w",encoding="utf-8")   
f.write(acumTodo)
f.close()
    
    
    
    
    
    
    
    
    
    
    
    

