# SpyPartyDraft

This is a tool designed for running web-based drafts for [SpyParty](http://www.spyparty.com) tournaments.  I wrote this mostly as an experiment with WebSockets (and as a reminder that I should not be anywhere near front-end HTML code because I can't make things pretty).  Turned out pretty well for just a quick experiment.  The code definitely needs some cleanup and there's a few TODO things I'd like to accomplish, but for now, I'm pretty happy.

This project was built in Python and JavaScript.  For Python, I am using the [Flask microframework](http://flask.pocoo.org) (my first project with that!) and the [Flask-SocketIO](http://flask-socketio.readthedocs.org) add-on.  The JavaScript code uses [JQuery](https://jquery.com) (of course), [Bootstrap](http://getbootstrap.com) (not that you could tell by looking at it), and [socket.io](http://socket.io) for web sockets.  I didn't really look up any best practices or anything because I was on vacation when I did this ("why not code on vacation?" I always say) and just kind of tried to figure out everything for myself.  I would definitely organize things a _LOT_ better if I were to do it all again.
 
# Running Locally
 
You shouldn't have too much trouble running this locally if you'd like.  Clone this repo, install all the dependencies using ```pip install -r requirements.txt``` (probably want to do this in a virtualenv), then just ```python SpyPartyDraft.py```

# TODO List

1. A not-terrible UI
2. Some display bugs
3. Massive code cleanup
4. Ability to rejoin draft in progress

# Contact the author

Best way to get a hold of me is on Twitter [@LtHummus](https://twitter.com/LtHummus)

# Thank you list

* [aforgottentune](https://twitter.com/aforgottentune) -- For help with testing and fixing my typos
* [checker](https://twitter.com/checker) -- For making the awesome game SpyParty
* [KrazyCaley](https://twitter.com/krazycaley) -- For creating the SpyParty Competitive League
* sgnurf -- For the contribution to support multiple draft types
* Everyone in the SpyParty community -- For being awesome (and the Canada of online communities)
* Paradise Village in Nuevo Vallarta, Nayarit, Mexico -- Because why waste a good vacation without doing some coding?
