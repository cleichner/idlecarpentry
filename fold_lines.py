from Tkinter import *
import OrderedDict

root=Tk()

text=Text(root)

lorem='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus pulvinar mattis purus, quis rutrum lectus rhoncus ut. Nulla dolor lectus, dapibus sed ullamcorper nec, vestibulum adipiscing purus. Sed consectetur, lacus ut placerat tempus, sapien quam viverra enim, vel venenatis ante lectus ut tortor.  Mauris laoreet sem id magna volutpat mattis. Aliquam eleifend tempor elit, ut pharetra nibh pellentesque nec. Pellentesque ac libero a justo scelerisque iaculis. Morbi dapibus enim id turpis facilisis tempor. Sed laoreet, neque at scelerisque lobortis, quam est aliquet urna, sed commodo ante sem eu odio. Nunc facilisis ipsum sed quam tincidunt viverra. Quisque eu augue dui, in pretium odio. Suspendisse potenti. Donec mattis ornare suscipit. Etiam a magna sapien.  Morbi vitae ligula lacus, vel iaculis enim. Curabitur sem lacus, viverra non bibendum nec, auctor sit amet nulla. Cras venenatis lectus aliquam nibh placerat pharetra. Vivamus dolor metus, sodales nec sollicitudin sit amet, varius sit amet libero.

Suspendisse quis sem tortor, sit amet mollis felis. Aliquam tincidunt viverra est, non dictum lorem tristique non. Nunc cursus, dolor eget hendrerit suscipit, nisl leo sollicitudin urna, sed scelerisque nulla sapien eget odio.  Vestibulum ipsum justo, imperdiet at blandit tincidunt, varius et turpis.  Quisque in arcu vitae magna dapibus accumsan. Nam venenatis orci id eros adipiscing consectetur. Sed convallis lorem non massa gravida interdum. Duis neque orci, egestas non suscipit in, dictum vitae nulla. Vivamus ac sapien arcu, at molestie dolor. Morbi dolor massa, gravida et porta molestie, placerat non elit.  

Nullam viverra, quam vitae lacinia commodo, nisl lacus iaculis purus, eu cursus est nunc eu metus. Donec vel massa sit amet dui dignissim ornare. Nullam id varius eros. Suspendisse blandit ultricies tempus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Mauris a lacus eget elit vestibulum hendrerit quis non orci. Donec quis luctus diam.  Nulla et quam enim, sit amet eleifend mi. Proin sed fermentum odio. Suspendisse potenti. Sed mollis odio sit amet quam gravida vitae hendrerit lectus bibendum.  Donec eros urna, tincidunt in interdum sit amet, pulvinar quis sapien. Integer tristique semper volutpat. Donec et odio in felis aliquet cursus. Pellentesque et velit urna, id gravida erat. Proin mauris felis, dapibus eget rutrum ut, elementum lacinia dolor. Proin iaculis ligula quis felis rhoncus vehicula vestibulum dui fermentum. Maecenas ac nibh orci, consequat tristique quam.  Etiam eget augue est. Pellentesque feugiat molestie dignissim.  ''' 

text.pack(side=TOP, fill=BOTH, expand=1)
folded_lines=OrderedDict.OrderedDict()
fold_length=50

for line in lorem.split('\n'):
    folded_lines[line[:fold_length]]=line+'\n'

for folded_line in folded_lines:
    text.insert(INSERT, folded_lines[folded_line]+'\n')

insert_line=None

def fold():
    text.delete('1.0', END)
    for folded_line in folded_lines:
        text.insert(INSERT, folded_line+'...\n')

def unfold():
    text.delete('1.0', END)
    for folded_line in folded_lines:
        text.insert(INSERT, folded_lines[folded_line])

fold_button=Button(root, command=fold, text='Fold All')
unfold_button=Button(root, command=unfold, text='Unfold All')

fold_button.pack()
unfold_button.pack()

root.mainloop()
#GOOD TRICK: text.tag_add("BREAK", "%d.0" % lineno, "%d.0" % (lineno+1))
