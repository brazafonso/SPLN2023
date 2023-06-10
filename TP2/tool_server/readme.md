# **Tool Server Generator**

Tool Server Generator is a python program that allows the seamless creation and possible deployment of servers that host tools runable from a bash (ex.: unix filters, scripts, programs, etc.).   
This program receives a file with the configuration for the server, from its initiating parametres such as the hosting port, to the tools to provide and some simple visual options to change the site's appearence. It does not however, install the provided tools, meaning that they need to be available from the start in the system that hosts the server.  
  
The server is created using *Node.js* and *express-generator*.

## **Dependencies**
The server will be generated using *Node.js*, which needs to be version 10.5 or above, so as to support *worker_threads*. All other *npm* requirements are installed by the program.  

To expose the server to a public url, you can use the *ngrok* options, which assumes that *ngrok* is already installed and with the authentication done on the host machine.

## **Usage**

To start the program, simply run:  

        ts <configuration_file>

Where the *configuration_file* is a text file that follows the structure explained bellow, or a JSON that fulfills the expected parameters.

### **Options**


    -h, --help          show this help message and exit
    -s, --start_server  starts server automatically
    -ng, --ngrok        uses ngrok to expose port. Needs ngrok installed on the system, authenticated.

## **Configuration File**

The configuration file defines the initiating aspects of the server, but also all the tools that are to be provided and some visual configurations.  
In the text format it needs to follow the syntax perceivable from the examples. The order of the fields is important, as is the use of the proper delimeters (ex.: '* Servidor', '- Nome:', '--' between tools).

### **Server Options**

#### *Text File*

- Name: name of the server.
- Directory: directory where the server will be created and run from.
- Port: port of the server.
- Route: base route of the website (optional - default '/').
- Workers: number of workers available to process requests (optional - default 1).

Example:

        * Servidor
        - Nome: Server
        - Diretoria: "test"
        - Porta: 15213
        - Rota: server\test
        - Trabalhadores: 2

#### *JSON*

The same type of fields are expected, the optional and obligatory are similar. Only the keys are differente.  
Example:

        {
            "nome" : "Server",
            "diretoria" : "test",
            "porta" : "15213",
            "rota" : "server\test",
            "workers" : 1,
        }

### **Tools options**

#### *Text File*

- Family : the family of the tool. This allows to group similar tools, or different calls of a tool together. Will determine its route.
- Title : the name of the specific tool. Will determine it's route. 
- Description : description of the tool.
- Command: command to run the tool with the specific variable (by the user) inputs delimeted using the exclusive word 'INPUT<number>'.
- Inputs: for each tool, their variable inputs need to be explicitly configured, otherwise they will be treated in the command as plain text. (optional)
    - Name: input name. (optional)
    - Description: input description. (optional)
    - Type: input type (STR|NUM|FILE).

Example:

    * Ferramentas
    --
    - Família:Grep
    - Título: "Grep"
    - Descrição: "grep  searches  for  PATTERNS in each FILE.  PATTERNS is one or more patterns separated by newline characters,
    and grep prints each line that matches a pattern.  Typically PATTERNS should be quoted when grep is used in  a
    shell command."
    -Comando: cat INPUT1 | grep INPUT2
    -Inputs:
        - INPUT1: 
            - Nome : file
            - Descrição : "File to search for the pattern"
            - Tipo : FILE
        - INPUT2: 
            - Nome : pattern
            - Descrição : "Pattern to search"
            - Tipo : STR

Each tool needs to be delimetd by '--'.


#### *JSON*
The same field requirements apply.


        "ferramentas" : {
        "Grep" : {
            "Grep" : {
                "descricao" : "grep  searches  for  PATTERNS in each FILE.  PATTERNS is one or more patterns separated by newline characters,
    and grep prints each line that matches a pattern.  Typically PATTERNS should be quoted when grep is used in  a
    shell command.",
                "comando" : "cat INPUT1 | grep INPUT2",
                "inputs" : [
                    {
                        "id": "INPUT1",
                        "opcoes" : {
                            "nome" : "file",
                            "descricao" : "File to search for the pattern",
                            "tipo" : "FILE"
                        }
                    },
                    {
                        "id": "INPUT2",
                        "opcoes" : {
                            "nome" : "pattern",
                            "tipo" : "STR",
                            "descricao" : "Pattern to search"
                        }
                    }
                ]
            }
        }
    }

### **Visual options**

The visual options are totally optional.

#### *Text File*

- Favicon : website favicon.
- Colors : configure website pallete.

Example:

    * Visuais
    - Favicon : "image.png"
    - PrimaryBgColor : #000
    - SecondaryBgColor : #fff
    - PrimaryTextColor : #fff
    - SecondaryTextColor : #3f51b5
    - LabelColor : #3f51b5
    - BorderColor : #9e9e9e

All the color options are present in the example above.

#### *JSON*

The same field requirements apply.

    "visuais":{
            "favicon" : "unknown2.png",
            "colors" : {
                    "primary_text_color" : "#000",
                    "secondary_text_color" : "#fff",
                    "primary_bg_color" : "#fff",
                    "secondary_bg_color" : "#3f51b5",
                    "label_color" : "#3f51b5",
                    "border_color" : "#9e9e9e",
                    }
        }

Server configuration file examples are available on the 'examples' folder.



