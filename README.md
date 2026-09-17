# FURTRATOR - Sort your nasty stuff!
This project was created with aims to sort local stored stuff

## Sorting
It's sorting by follow categories:

| Category   | Description 
| -          | -           
| SFW        | General SFW 
| FURRY SFW  | Furry themed SFW 
| NSFW       | General NSFW 
| FURRY NSFW | Furry themed NSFW 
| OTHER      | General files and etc

## Sorting params
Out of the box script has next weigth params for the used models to do sort things:

#### Threshold
| Type  | Default | Variable     | Description            
| -     | -       | -            | -                      
| NSFW  | 0.01    | NSFW_THRESH  | Higher value - stricter
| FURRY | 0.38    | FURRY_THRESH | Higher value - stricter

#### Aggregation
| Type  | Default | Variable          | Description                                        
| -     | -       | -                 | -                                         
| NSFW  | max     | NSFW_AGGREGATION  | For medium result is `mean` and `max` for agressive
| FURRY | mean    | FURRY_AGGREGATION | For medium result is `mean` and `max` for agressive

## Videos and Animated images
This sorting script is also supports videos and animated images.

| Param           | Default | Variable                                           | Description
| -               | -       | -                                                  | -
| Frames playtime | 250     | VIDEO_LONG_PLAYTIME_FRAMES_COUNT                   | Total frames to pick
| Gauss algoritm  | True    | VIDEO_USE_GAUSS_HANDLER_ALGORITM_FOR_LONG_PLAYTIME | Using custom-made gauss algo to pick keyframes (Graph 1.) instead of linear
| Frames count    | 40      | VIDEO_KEYFRAMES_COUNT                              | Count of frames to pick
| Frames offset   | 5       | VIDEO_KEYFRAMES_OFFSET                             | Random offset from selected frame
| Debug           | False   | DEBUG_VIDEO                                        | Saves keyframes grid

<div align="center">

```tex
_/\_
_/    \_
_/\_     /        \     _/\_
_/      \__/          \__/      \_
```
<p><i>Graph 1. Custom-maded graph to fast-pick best keyframes</i></p>
</div>

## UI
Script has TUI that shows sorting progress.

| Param           | Default | Variable | Description
| -               | -       | -        | -
| Enable TUI      | True    | USE_UI   | Enables TUI render instead of simple print-output

## In The End
Special thanks to:
 - MaestroDDOS - advices
 - Shelest - advices