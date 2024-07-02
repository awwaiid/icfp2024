# icfp2024

Our team's collaboration for [ICFP Contest 2024](https://icfpcontest2024.github.io/).

* Team name: Kirby's Star Allies (thanks to Errol!)
* Participants: Brock, Jason, Russell, a bit from Mario, and Mike cheering us on
* Technology: Mostly Pythong. Lots of github-copilot and Claude.
* Brock visited Jason on the west coast, others collaborating over Discord

## Strategy Notes
* Commit early, commit often! Straight to `main`
* Previous year strategies
  * Lots of independent CLI tools
  * Unix pipes in/out with JSON (line-oriented if streaming)
  * Visualize the problem
  * Tools/UI to solve the problem manually
  * Solve the problem with a bot
  * Combine bots
  * Build a way to score -- both locally and globally
    * Sometimes this uses the org API to score, but local scoring is better for algorithms
  * If it is a collection of problems, keep a folder of problems and solutions
  * Put the most important info in the filename -- the problem identifier and score
  * Scripts to submit (individual or bulk) standalone solutions to organizers
* This year
  * The overall problem pretty cleanly divided into parts
  * Russell built the initial interpreter
  * Interpreter for the ICFP-lang
    * Brock made it general purpose
    * Then built an experimental to-python compiler, but it didn't make it much faster
  * Lambdaman
    * 2D-maze grid like pacman eating dots
    * Russell solved some by hand but mostly built a solver using A* and several heuristics and sub-goals
  * Spaceship
    * An astroids style game with targets to hit
    * Jason solved this by hand but mostly built a solver
    * Uses heuristics on next-target selection, velocity adaptation, tries to prevent oscillation
  * 3d
    * This is a 2D grid + time programming language and a series of programs to implement
    * Mario, Jason, and Brock solved these by hand
  * efficiency
    * A series of harder and harder problems to run through the interpreter
    * It was a trick though, you need an optimizing compiler or something to actually solve these
    * So we decompiled them and solved several by hand
    * Brock solved 1-4
    * Mario or someone solved 5
* A fun time was had by all!!!!

[]!(./rank.png)

