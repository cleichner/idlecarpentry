from Tkinter import *
import OrderedDict

root=Tk()

text=Text(root)
text.config(width=80)

lorem='''    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus pulvinar mattis purus, quis rutrum lectus rhoncus ut. Nulla dolor lectus, dapibus sed ullamcorper nec, vestibulum adipiscing purus. Sed consectetur, lacus ut placerat tempus, sapien quam viverra enim, vel venenatis ante lectus ut tortor.  Mauris laoreet sem id magna volutpat mattis. Aliquam eleifend tempor elit, ut pharetra nibh pellentesque nec. Pellentesque ac libero a justo scelerisque iaculis. Morbi dapibus enim id turpis facilisis tempor. Sed laoreet, neque at scelerisque lobortis, quam est aliquet urna, sed commodo ante sem eu odio. Nunc facilisis ipsum sed quam tincidunt viverra. Quisque eu augue dui, in pretium odio. Suspendisse potenti. Donec mattis ornare suscipit. Etiam a magna sapien.  Morbi vitae ligula lacus, vel iaculis enim. Curabitur sem lacus, viverra non bibendum nec, auctor sit amet nulla. Cras venenatis lectus aliquam nibh placerat pharetra. Vivamus dolor metus, sodales nec sollicitudin sit amet, varius sit amet libero.
    Suspendisse quis sem tortor, sit amet mollis felis. Aliquam tincidunt viverra est, non dictum lorem tristique non. Nunc cursus, dolor eget hendrerit suscipit, nisl leo sollicitudin urna, sed scelerisque nulla sapien eget odio.  Vestibulum ipsum justo, imperdiet at blandit tincidunt, varius et turpis.  Quisque in arcu vitae magna dapibus accumsan. Nam venenatis orci id eros adipiscing consectetur. Sed convallis lorem non massa gravida interdum. Duis neque orci, egestas non suscipit in, dictum vitae nulla. Vivamus ac sapien arcu, at molestie dolor. Morbi dolor massa, gravida et porta molestie, placerat non elit.  
    Nullam viverra, quam vitae lacinia commodo, nisl lacus iaculis purus, eu cursus est nunc eu metus. Donec vel massa sit amet dui dignissim ornare. Nullam id varius eros. Suspendisse blandit ultricies tempus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Mauris a lacus eget elit vestibulum hendrerit quis non orci. Donec quis luctus diam.  Nulla et quam enim, sit amet eleifend mi. Proin sed fermentum odio. Suspendisse potenti. Sed mollis odio sit amet quam gravida vitae hendrerit lectus bibendum.  Donec eros urna, tincidunt in interdum sit amet, pulvinar quis sapien. Integer tristique semper volutpat. Donec et odio in felis aliquet cursus. Pellentesque et velit urna, id gravida erat. Proin mauris felis, dapibus eget rutrum ut, elementum lacinia dolor. Proin iaculis ligula quis felis rhoncus vehicula vestibulum dui fermentum. Maecenas ac nibh orci, consequat tristique quam.  Etiam eget augue est. Pellentesque feugiat molestie dignissim.  ''' 

text.pack(side=TOP, fill=BOTH, expand=1)
fold_length=77

#keys are full lines, values are folded lines
folded_lines=OrderedDict.OrderedDict()

#keys are folded lines, values are unfolded lines
unfolded_lines=OrderedDict.OrderedDict()

for line in lorem.split('\n'):
    folded_line=line[:fold_length]+'...\n'
    unfolded_line=line+'\n'
    
    folded_lines[unfolded_line]=folded_line
    unfolded_lines[folded_line]=unfolded_line

for full_line in folded_lines:
    text.insert(INSERT, full_line)

def manipulator(dictionary):
    def dictionary_replace():
#the +1c is to get the newline
        current=text.get('insert linestart', 'insert lineend+1c')
        text.delete('insert linestart', 'insert lineend+1c')
        try:
            text.insert(INSERT, dictionary[current])
        except KeyError:
            text.insert(INSERT, current) 

    return dictionary_replace

button_frame=Frame(root)
fold_button=Button(button_frame, command=manipulator(folded_lines), text='Fold')
unfold_button=Button(button_frame, command=manipulator(unfolded_lines), text='Unfold')

button_frame.pack(side=TOP)
fold_button.pack(side=LEFT)
unfold_button.pack(side=LEFT)

root.mainloop()
#GOOD TRICK: text.tag_add("BREAK", "%d.0" % lineno, "%d.0" % (lineno+1))
