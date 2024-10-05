def a_to_m(text):
  a_to_m={'a':'.-','b':'-...','c':'-.-.','d':'-..','e':'.','f':'..-.','g':'--.','h':'....','i':'..','j':'.---','k':'-.-','l':'.-..','m':'--','n':'-.','o':'---','p':'.--.','q':'--.-','r':'.-.','s':'...','t':'-','u':'..-','v':'...-','w':'.--','x':'-..-','y':'-.--','z':'--.'}
  text=text.lower() 
  text=text.split()
  for i in text:
    for j in i:
      print(a_to_m[j],end=' ')
    print(' ')
a=input('Enter the text: ')
a_to_m(a)

def m_to_a(text):
  m_to_a={'.-':'a','-...':'b','-.-.':'c','-..':'d','.':'e','..-.':'f','--.':'g','....':'h','..':'i','.---':'j','-.-':'k','.-..':'l','--':'m','-.':'n','---':'o','.--.':'p','--.-':'q','.-.':'r','...':'s','-':'t','..-':'u','...-':'v','.--':'w','-..-':'x','-.--':'y','--.':'z'}
  text=text.lower() 
  text=text.split('  ')  
  for word in text:
    letters = word.split()  
    for morse_code in letters:
      print(m_to_a[morse_code], end='')
    print(' ', end='')  
b=input('Enter the Morse code: ')
m_to_a(b)