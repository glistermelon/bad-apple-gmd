# Bad Apple in Geometry Dash

## Overview

The primary goal for this project was to create a version of Bad Apple in Geometry Dash that was satisfy these three goals:
1. Match the resolution of the original video (512x384)
2. Have more color depth than just black and white
3. Be runnable on at least a high-end PC

In order to accomplish these, I had to give up on getting it to run at the original video's 30 FPS. See down below for information about the lag.

Currently, the generated level runs at about ~10 FPS on my laptop, so the script is configured to use that FPS. Setting the FPS higher is not going to make any noticeable difference unless your PC can handle it, and it would probably increase the level size.

## Previous Versions

#### WEG Fan's version (pixelated canvas)

**Video:** [YouTube](https://www.youtube.com/watch?v=DxO3S_phfL8)
**Details:** [Pastery](https://www.pastery.net/sgttcr/)
**Created:** July 2018 (GD 2.1)
**Resolution:** idk @ 30 FPS, 1 bit color depth

As far as I can tell, this is the first recreation. I believe this version uses the simplest approach out there, where you take all the group IDs (only 999 in 2.1), assign one to each pixel, and use toggle triggers to turn the right pixels on and off each frame.

#### GD Colon's version (pixelated canvas)

**Video:** [YouTube](https://www.youtube.com/watch?v=c6NMa716-Ek)
**Created:** February 2021 (GD 2.1)
**Resolution:** 50x38 @ 30 FPS, 1 bit color depth

This is the next simplest approach out there, where you take all the group IDs *and* all the color channels and have one pixel for each group/channel. Then it's simple to update the canvas by referencing each pixel independently.

The obvious drawback to this method is that the resolution is very limited. However, the limited resolution and simple method causes basically zero lag, so it probably runs at a smooth 30 FPS.

If you want more details, go read the video description. Admittedly, I didn't read it; I'm just speculating all over the place.

#### bombie's version (ASCII)

**Video:** [YouTube](https://www.youtube.com/watch?v=a2WQQXOzzg8)
**Details:** [GitHub](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqa2lxdWQ5LUxsVDJIX0paYjhSUHJhVm9nZFVwQXxBQ3Jtc0tuMWRvUVppQTlDbkp4cDV2Z243Yjc3c25HeS1XSkZSblctY2ttOXlBal9QcE5aeUdSbkZKMmFjb19QbUVNcm5SSjNKUVpvTjFUV1o4VFRRRnROSzRVS1VBM25LVUhGWG1yVFpVdVhKN0liSVNVdWI1WQ&q=https%3A%2F%2Fgithub.com%2Fitsmebombie%2Fascii-video&v=a2WQQXOzzg8)
**Created:** March 2023 (GD 2.1)

From what I understand, this uses SPWN's functionality for printing text to create an animation. But, I have no idea what approach spu7nix took for printing in SPWN so I honestly don't really know how it works.

Once again, the primary limitation is resolution, but FPS should be good. It's seems obvious that the goal of this project is more about the cool ASCII art implementation than trying to accurately render the video, of course, but I still thought it's worth including here.

#### riorio805's version (quads)

**Video:** [YouTube](https://www.youtube.com/watch?v=pnwec3SUEi0)
**Created:** January 2024 (GD 2.2)
**Resolution:** N/A @ 7.5 FPS, 1 bit color depth

I don't know that much about how this one works either but just from the statement that it uses gradient's I feel like it's fair to assume it probably takes the video, transforms it into a set of quads per frame, and then uses move triggers to rerarrange gradients such as to render the quads, thus rendering the video.

The big benefit of using quads is that you get a really good resolution without a huge number of objects. There are numerous unavoidable drawbacks though. You have to find linear approximations for curves, and in most cases you will need to sacrifice accuracy to the original video. Assuming it does use move triggers, you have to move a lot of stuff per frame, which is probably why it was limited to 7.5 FPS (not that mine does much better...). Furthermore, as riorio noted in the description, there are some weird visual glitches in the playback too, but I don't know why.

#### My previous version (RLE-based rows)

**Video:** [YouTube](https://www.youtube.com/watch?v=C2hMZtQykBA)
**Details:** [GitHub](https://github.com/glistermelon/old-gd-bad-apple)
**Created:** March 2024
**Resolution:** 512x384 @ 30 FPS, 1 bit color depth (**disclaimer below**)

You can read more about this one on the linked GitHub page, but the biggest issue is that it might as well be purely theoretical. I had to use a rendering engine with 30 FPS lock delta in order to actually get a video, because it is so computationally expensive to run that it just instantly freezes on my PC. What made this approach unique is that, thanks to sequence trigger abuse, it uses a very low number of objects. Honestly, though, I don't think this is really impressive because it becomes a lot easier to accomplish a goal when actually being able to play the level isn't a requirement.

#### Masterous112's version (pixelated canvas)

**Video:** [Reddit](https://www.reddit.com/r/geometrydash/comments/1es98e5/28_million_objects_bad_apple_in_geometry_dash_id/)
**Created:** August 2024
**Resolution:** 100x75 @ 30 FPS, 4 bit color depth

Okay so, for this one, I also don't know exactly how it works, so everything I'm saying or assuming is based on Masterous112's comments on the Reddit post I linked.

This is the first recreation I know that successfully pulls off nonbinary colors. It uses alpha triggers each frame to update pixels on the canvas, referencing by group ID, which is way more effective in 2.2 with the increased group ID limit.

In my opinion, of all preexisting versions, this is the best one (not to say that mine is necessarily better). It runs very smoothly at >30 FPS on most devices and has the best color depth of any version. The huge drawback to this method, however, is that the use of one alpha trigger for every pixel change causes the level to have a huge number of objects.

## This Version's Stats

**Resolution:** 512x384 (matching original video)

**FPS:** 10 FPS
* This is pretty disappointing, but it's due to how RobTop handles updates, not really design limitations. See the section about lag below for more details.

**Color depth:** 4 bits.
* This is a design limitation. Pushing the color depth higher makes it use way more groups which inflates the level size due to the mechanism used to avoid running out of group IDs.

## My Approach

My primary goal was for the recreation to have a high resolution but still be actually playable. By "playable", I just mean with enough FPS for me to record a video by just playing the level instead of using a showcase tool.

With a 512x384 resolution, consisting of nearly 200,000 pixels, it is impossible to use group IDs and color IDs to reference each pixel distinctly using one ID. Even if you could, you would often be packing more than 100,000 triggers into a single frame update, which would probably just freeze the game.

For my approach, instead of assigning a group ID to each pixel for unique updates, each pixel is assigned a list of group IDs, each of which represents a change to a particular color at a particular frame. Each frame, for each new colors that needs to appear in the updated pixels, a single pulse trigger targets the pixels that need to change to that color via a single group ID. This avoids computational lag due to triggers, as, even with the highest possible color depth, at most 256 pulse triggers would be created for one update.

At a really simple overview level, that's pretty much it.

# Specific Implementation Details

## Creating the canvas

The video is played on a 512x384 canvas of 196,608 objects. However, if you create the canvas naively, only a small fraction of it actually renders, and the rest is just mysteriously invisible. This is actually because RobTop renders objects using `CCSpriteBatchNode`, which provides sprite vertices to OpenGL in 16-bit integers. One sprite has four vertices and there are only 65,536 distinct 16-bit integers, so the batch node can only handle 16,384 objects.

There is a way around this limitation, thankfully. RobTop actually uses a bajillion instances of `CCSpriteBatchNode` at the same time. Most of them are useless for these circumstances, but there are still 18 useful ones. There are 9 for opaque objects on different Z layers, and another 9 for objects with a blending color channel on different Z layers. So, the canvas is actually created in sections of objects with different Z layers and one of two color channels to ensure that the batch node sprite limit is not exceeded.

There is an additional complication, though. I don't know the specific reason why, but if you perfectly space out the objects on the canvas, you will often see a few vertical gaps in the canvas. As far as I can tell, they are entirely visual defects, as the objects are actually perfectly aligned. Nonetheless, they go away if you scale up the pixels just a little bit so the pixels actually overlap a bit. The problem is, overlapping blending pixels create more weird line segments where they overlap, which is undesirable.

So, the canvas is actually created in sections consisting of 2x2 tiles. Each tile has two opaque objects and two blending objects in the same Z layer arranged in a checkerboard pattern, so that the opaque objects hide the overlap between the blending objects. If you tile the whole canvas like this, you still get blending pixels on one Z layer that are alongside opaque objects on another layer thereby still causing defects. So, all the tiles in one Z layer are placed in a section which is separated from the next section by a solid line of opaque objects.

That's pretty much it. For actually focusing on the canvas, I just put the game in platformer mode and used a zoom trigger to zoom way out and a static camera trigger to focus the camera at the center of the canvas.

## Pixel substitution

The biggest caveat to this method is that, incredibly annoyingly, RobTop has an arbitrary limit of 10 for the number of group IDs that an object can have. A single pixel has to change more than 10 times, so this is a problem.

The solution I came up with is as follows. If a pixel has 10 group IDs all for color changes, then it becomes useless when they're finished. So, pixels are limited to 9 group IDs for color changes. When a pixel needs to change on a frame update but it already has 9 assigned group IDs, the 10th assigned group ID is targeted by a move trigger which simultaneously removes the pixel from the canvas and replaces it with a new one. Note that since the new one typically has to be moved on-canvas at one time and later moved off-canvas at another time, it is limited to 8 group IDs for color changes. It is necessary to keep pixels that are not in use either disabled via toggle triggers or off-screen to prevent lag; evidently, I went with the latter.

## Staying within the group ID limit

Let $n$ be however many shades of grey are in use. Then, a single update, at the moment, uses as many as $n + 1$ groups per frame: $n$ for color changes and one for pixel substitution. For low values of $n$, you actually get pretty good video quality that still takes a pretty long time to use up all the group IDs. I primarily experimented with a 3 bit color depth (8 shades of grey), and it took until more than half way through the video to run out. Still, it's a problem that has to be solved.

My initial idea was as follows. Eventually, all the pixels using a certain group ID will have moved off-canvas, at which point that group ID can be reused. However, a major caveat is that it can only be reused by objects that were not on-canvas at any point during the same time in the original set of objects using the group ID were set to the color associated with the group ID. This limitation is fine on its own, and I had code to handle this, but there ended up being another limitation that completely destroyed this approach. Pulse triggers actually prioritize some groups over others, which is a huge problem if you want to reuse a group ID but the object you want to reuse it on has a group ID with a greater priority than the one you want to reuse. In the editor, this priority is determined per-object by the order of the object's group IDs in the object's memory, so, this approach worked perfectly in the editor. However, when you actually play the level, for seemingly no good reason, the priority is determined by ascendingly sorting an object's group IDs. The consequence of this is a new limitation, that a group ID cannot be reused by an object unless all of the group IDs it has already been assigned are less than the one to be reused. This is a huge limitation which makes the entire idea of reusing group IDs in this way completely worthless. Recall this is entirely due to yet another arbitrary design decision RobTop likely implemented for no good reason.

Regardless, I came up with another way to get around the group ID limit. Annoyingly, it causes way more bloating in the level's object count than the previous method would have, but it was the next best thing I could think of. In order to avoid those priority issues, group IDs are pulled from an ascending stack. The script detects when it is about to run out of group IDs, and initiates a "reset period." The goal of the reset period is to replace every pixel on the canvas with a new pixel, thereby freeing up all the group IDs. However, replacing every pixel in a single move call causes enough lag to screw up the playback, so it is done in a series of move calls across the reset period.

There are some additional technical details to the reset period, of course. Recall that there are issues when an object using a group ID is on-canvas at the same time as another object reusing the group ID. Since we're resetting the canvas in chunks, we are progressively bringing in new objects that reuse group IDs while old objects already using those IDs are still on-canvas. This causes a weird effect where a line basically moves across the canvas with everything on one side of it corrupted until it reaches the end of the canvas. Recall $n$ from earlier. To get around this, $2n$ group IDs are assigned to be used only by objects being added during a reset period. The $2n$ group IDs is actually split into two sets of $n$ and $n$ and the system alternates between each set for each reset period, since only using one set leads to the same issue we are trying to work around.

Lastly, additional stuff has to be implemented for reusing group IDs for move triggers. A group ID that has been used for a color change can be reused for a move trigger once the object originally using the group ID has gone off-canvas, but a group that has already been used to move pixels cannot be reused for a color change. Well, technically it can, but it isn't practical since you would have to offset the moves in advance for every wave of new objects. I could be wrong about that though; let me know if you think otherwise and think there's good reason to care about it. Regardless, to deal with this, once a group ID is used for a movement, it is placed in a pool where it cannot be reused for color changes, but can be reused for movements. Since group IDs for color changes have to be assigned ascendingly to prevent the priority issues from earlier, when a group ID needs to be claimed for a move trigger, it is popped from the top end of the available group ID stack (the group IDs for color changes are taken from the bottom, since they ascend). So, the stack of group IDs for color changes shrinks over time but eventually stabilizes. After each reset period, the stack for all group IDs is replenished.

Also, note that, after the reset period, all the pulse triggers that were previously in use need to be stopped. This is done so using a stop trigger targetting a control ID. However, this is not the best way; see possible optimizations for more info.

## Possible optimizations?

#### Canvas resets

The "canvas reset" system I used was really the reasonable thing I came up with after my first approach failed. I was extremely pissed off that the first approach failed over a pointless technicality and I was annoyed that I had to be thinking about how to get around the group ID limit at all since I had just thought that problem was in the past. Basically, I really haven't put that much thought into systems for staying under the group ID limit. There could be something better than the system I have now.

#### Pulse trigger stopping

Pulse triggers are currently stopped using a stop trigger and a control ID. One could just set the pulse trigger hold durations such as to align with wherever the stop trigger is placed and then eliminate the stop trigger entirely. However, this would be annoying to implement and I don't know if it's worth the benefit. I believe pulse triggers are a very small portion of the file size and are not the primary cause of playtime lag.

## Tracing lag

Most of the lag can be traced to `GJBaseGameLayer::updateVisibility`, but I've looked over the decompilation and it doesn't seem like there's much I can do about it.