from bs4 import BeautifulSoup
import sys
import json

def transform(input_fn, env_fn, output_fn):
    f = open(env_fn, 'r')
    env = json.load(f)
    f.close()
    
    f = open(input_fn, 'r')
    soup = BeautifulSoup(f, features='lxml')
    f.close()
    
    output_tree = process(soup, env)
    
    content = output_tree.prettify()
    print(content)
    f = open(output_fn, 'w')
    f.write(content)
    f.close()
    
def process(soup, env):
    
    for child in soup.body.children:
        # <body> WE ARE HERE </body>
        
        
        # FOR <h1> TAG
        if child.name == 'h1':
            # <body><h1> WE ARE HERE </h1></body>
            for h1child in child.children:
                if h1child.name == 'print':
                    # <h1><print> WE ARE HERE </print></h1>
                    h1_var = soup.h1.print['var']
                    soup.h1.print.extract()
                    soup.h1.insert(1, env[h1_var])
        
        
        # FOR <p> TAG
        if child.name == 'p':
            # <body><p> WE ARE HERE </p></body>
            for pchild in child.children:
                if pchild.name == 'for':
                    # <p><for> WE ARE HERE </for></p>
                    p_list = pchild['list']
                    p_iter = pchild['iter']
                    for for_child in pchild.children:
                        if for_child.name == 'print':
                            # <p><for><print> WE ARE HERE </print></for></p>
                            for p_iter in env[p_list]:
                                soup.p.append(p_iter)
                                soup.p.append("\n")
                        elif for_child.name == 'if':
                            # <p><for><if> WE ARE HERE </if></for></p>
                            for_child_var = for_child['var']
                            for_child_val = for_child['val']
                            for p_iter in env[p_list]:
                                if p_iter == for_child_val:
                                    soup.p.append(p_iter)
                        elif for_child.name == 'else':
                             # <p><for><else> WE ARE HERE </else></for></p>
                            for_child_var = for_child['var']
                            for_child_val = for_child['val']
                            for p_iter in env[p_list]:
                                if p_iter != for_child_val:
                                    soup.p.append(p_iter)
                    # remove the child of <pri> after appending
                    pchild.extract()
        
        
        # FOR <ul> TAG
        if child.name == 'ul':
            # <body><ul> WE ARE HERE </ul></body>
            for ul_child in child.find_all():
                if ul_child.name == 'for':
                    # <ul><for> WE ARE HERE </for></ul>
                    ul_list = ul_child['list']
                    ul_iter = ul_child['iter']
                    
                    if ul_child.find('li') != None and ul_child.find('ol') != None:
                        # <ul><for> WE ARE HERE </for></ul>
                        if ul_child.li.find('print') != None:
                            # <ul><for><li> WE ARE HERE </li></for></ul>
                            li_var = ul_child.li.print['var']       
                        for ol_child in ul_child.find_all():
                            if(ol_child.name == 'for'):
                                ol_var = ol_child.print['var']
                                # <ul><for><ol><for> WE ARE HERE </for></ol></for></ul>
                                ol_list = ol_child['list']
                                ol_iter = ol_child['iter']          
                        # remove <for> child and its nested elements
                        ul_child.extract()
                        if li_var == ol_var: 
                            for ul_iter in env[ul_list]:
                                li = soup.new_tag("li")
                                li.string = ul_iter
                                soup.ul.append(li)
                
                                ol = soup.new_tag("ol")
                                for ol_iter in env[ol_list]:
                                    li2 = soup.new_tag('li')
                                    li2.string = ul_iter
                                    ol.append(li2) 
                                soup.ul.append(ol)
                    
                    elif ul_child.find('li') != None and ul_child.find('ol') == None:
                        # <ul><for> WE ARE HERE </for></ul>
                        for li_child in ul_child.li.children:
                            if li_child.name == 'print':
                                # <ul><for><li><print> WE ARE HERE </print></li></for></ul>
                                li_var = li_child['var']
                                # remove <for> child and its nested elements
                                ul_child.extract()
                                for ul_iter in env[ul_list]:
                                    li = soup.new_tag("li")
                                    li.string = ul_iter
                                    soup.ul.append(li)
        
        
        # FOR <ol> TAG
        if child.name == 'ol':
            # <body><ol> WE ARE HERE </ol></body>
            for ol_child in child.find_all():
                if ol_child.name == 'for':
                    # <ol><for> WE ARE HERE </for></ol>
                    ol_list = ol_child['list']
                    ol_iter = ol_child['iter']
                    for for_child in ol_child.children:
                        if for_child.name == 'else':
                            # <ol><for><else> WE ARE HERE </else></for></ol>
                            else_var = for_child['var']
                            else_val = for_child['val']  
                            for else_child in for_child.children:
                                if else_child.name == 'li':
                                    # <ol><for><else><li> WE ARE HERE </li></else></for></ol>
                                    for li_child in else_child.children:
                                        if li_child.name == 'print':
                                            # <ol><for><else><li></print> WE ARE HERE </print></li></else></for></ol>
                                            li_var = li_child['var']
                                            # remove <for> child and its nested elements
                                            ol_child.extract();
                                            for ol_iter in env[ol_list]:
                                                if ol_iter != else_val:
                                                    li = soup.new_tag("li")
                                                    li.string = ol_iter
                                                    soup.ol.append(li)   
        
                    
    
    #print(soup.prettify())
    return soup
    
def main():
    if len(sys.argv)!=4:
        print('Expected command: python %s<input-html><env-json><output-html>'%sys.argv[0])
        sys.exit(0)
        
    input_fn = sys.argv[1]
    env_fn = sys.argv[2]
    output_fn = sys.argv[3]
        
    print("%s + %s ==> %s"%(input_fn, env_fn, output_fn))
    transform(input_fn, env_fn, output_fn)
        
main()