import cv2
import json
import numpy as np
import argparse
import os

file_names = ["3913", "20190908_134913", "20190908_135102", "p40_20190821_122507", "vertical4"]

HEIGHT = 1000

def getPipsRegions(H, W, pipH, pipW, barW, sIH, sIW):

  pipH = int(pipH*1.1)
  pipW = int(pipW*1.01)

  topPipsRegions = []
  bottomPipsRegions = []

  
  for i in range(12):
    #shiftBarWidth
    sBW = 0 if (i < 6) else barW
    
    # TOP PIPS:
    pt_TL = (i*pipW + sBW + sIW,     sIH        )        # point TOP LEFT
    pt_BR = ((i+1)*pipW + sBW + sIW, sIH + pipH)    # point TOP RIGHT
    topPipsRegions.append([pt_TL, pt_BR])

    # BOTTOM PIPS:
    pt_TL = (i*pipW + sBW + sIW,        H + sIH - pipH )
    pt_BR = ((i+1)*pipW + sBW + sIW,    H + sIH)
    bottomPipsRegions.append([pt_TL, pt_BR])

  return topPipsRegions, bottomPipsRegions

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('input_path', type=str)
  parser.add_argument('output_path', type=str)

  args = parser.parse_args()
  input_path = args.input_path
  output_path = args.output_path
  if not os.path.exists(output_path):
    os.makedirs(output_path)
    
  for fname in file_names:

    with open(input_path+"/"+fname+".jpg.info.json") as fjson:

      data = json.load(fjson)
      img = cv2.imread("bgsamples/"+fname+".jpg")

      board_corners = data["canonical_board"]["tl_tr_br_bl"]
      (tl, tr, br, bl) = board_corners


      width = int(data["canonical_board"]["board_width_to_board_height"]*HEIGHT)
      pipLength = int(HEIGHT*data["canonical_board"]["pip_length_to_board_height"])
      
      BWtCW = data["canonical_board"]["bar_width_to_checker_width"]
      # width = 12checkers + 1bar 
      #        = 12checkers + 1(checkers*BWtCW)
      #        = checker ( 12+BWtCW)
      # checker = width/(12+BWtCW)
      checkerWidth = int(width/(12+BWtCW))
      checkerRadius = checkerWidth/2
      barWidth = int(checkerWidth*BWtCW)

      sH = 20 #shift HEIGHT
      sW = 20 #shigt width

      new_board_corners = [
        [0+sH, 0+sW], 
        [HEIGHT+sH, 0+sW],
        [HEIGHT+sH, width+sW], 
        [0+sH, width+sW]
      ]

      pts1 = np.array(board_corners, dtype=np.float32)
      pts2 = np.array(new_board_corners, dtype=np.float32)


      M = cv2.getPerspectiveTransform(pts1, pts2)
      img_p = cv2.warpPerspective(img, M, (width+2*sW, HEIGHT+2*sH)) 

      gray = cv2.cvtColor(img_p, cv2.COLOR_BGR2GRAY)

      boardContour = np.array([pts2], dtype=np.int32)

      circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, checkerWidth*0.8, 
            param1=100,
            param2=20,
            minRadius = int(checkerRadius*0.9), 
            maxRadius = int(checkerRadius*1.1))

      circles = np.uint16(np.around(circles))
                                                # (H, W, pipH, pipW, barW, sIH, sIW)
      topRegions, bottomRegions = getPipsRegions(HEIGHT, width, pipLength, checkerWidth, barWidth, sH, sW)

      counter = {
        "top": [0]*12,
        "bottom": [0]*12
      }

      for (xC, yC, rC) in circles[0,:]:
        found = False

        for i, reg in enumerate(topRegions):
          x1R = reg[0][0]
          x2R = reg[1][0]
          y1R = reg[0][1] 
          y2R = reg[1][1] 
          if ( x1R < xC <= x2R and y1R < yC <= y2R):
            counter["top"][i]+=1
            found = True

            cv2.waitKey(0)
            cv2.destroyAllWindows()

            break

        if (not found):
          for i, reg in enumerate(bottomRegions):
            x1R = reg[0][0]
            x2R = reg[1][0]
            y1R = reg[0][1] 
            y2R = reg[1][1] 
            if ( x1R < xC <= x2R and y1R < yC <= y2R):
              counter["bottom"][i]+=1

              break

      #print ("TOP:", counter["top"])
      #print ("BOT:", counter["bottom"], '\n')

      #for reg in (topRegions+bottomRegions):
      #  cv2.rectangle(img_p, reg[0], reg[1], color=(255,0,0), thickness=2)

      for xC, yC, rC in circles[0,:]:
        cv2.circle(img_p,(xC, yC),rC,(0,255,0),2)
        cv2.circle(img_p,(xC, yC),2,(0,0,255),3)

      cv2.drawContours(img_p, boardContour, -1, (0,0,255), 2)

      file_path = output_path+"/"+fname+".visual_feedback.jpg"
      cv2.imwrite(file_path, img_p)

      file_path = output_path+"/"+fname+".checkers.json"
      with open(file_path, 'w') as jf:
        json.dump(counter, jf, indent=4)
      jf.close()

      #cv2.imshow("Over the Clouds", img_p)
      #cv2.waitKey(0)
      #cv2.destroyAllWindows()

      # break

