# WARP AND FIND CHECKERS IN BACKGAMMON GAME WITH PYTHON AND OPENCV

### 
How to use it:
```
python warp_and_find_checkers <input_path> <output_path>
```
For each image in *input_path* folder:
* There must also be a *.info.json* file 
* Image type must me **.jpg** 


## QUESTIONS:

i) How well do you expect this to work on other images?
ii) What are possible fail cases of this approach and how would you address them?
iii) How would you implement finding the colors of the checkers and distinguishing which player the checker belongs to?

## ANSWERS:

### Items *i* and *ii*
It was perceived from the resulting model that, although the results obtained are satisfactory, in order to avoid failures, the following important features must be fulfilled:
* In code, set big height for output images, which increases accuracy on finding pip's areas, so that later determine which checkers belongs to which pips
* Consider that there are gaps between the pips, so this size may affects performance
* Have checkers as aligned as possible in a straight line
* Have pip's width as equal as possible to checker's width

### Item *iii*
To detect checker's colors: calculate the average pixels colors inside checkers contours. To distinguishing which player the checker belongs to, verify which are the two predominant colors on all over the board, an then associate them witch checkers colors.