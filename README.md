Website that can pull projection data from all major fantasy platforms (sleeper, yahoo, nfl, and espn) and compare them for accuracy.
Train an ML model to determine the best one/get a new projection based on the data analysis ("True projection").

With this new "true projection", add the ability to input sleeper league id and output betting lines. Stuff like odds to make playoffs, win ship, etc... 
Make the lines even, no edge to "the house" so people can bet amongst their leaguemates on how their team/other teams will perform.

Create account system so people can make bets, then login later to see if they hit.
Nullify bets if stupid trade happens (how to determine this...)

In the future it would be cool to enable betting with money on the site, charging a percentage-based fee for each bet. Example: league member #1 thinks he will make the playoffs, league member #2 thinks he will not. The line is even, and they each put $10 down on it. The winner would get $19, and I would get $1.

MVP:
- [ ] Pull projections from sleeper for each team
            Latest-year-ppr projections are now stored in the database. Need to get rosters and put it all together to get yearly team projections. Note: projections are no longer supported by sleeper API. I had to use a third-party wrapper to get the data. Messy code, should be cleaned.
- [ ] Process league's season projections with league settings
- [ ] Run a monte carlo simulation (10000+ sims)
- [ ] Calculate betting lines (sims making playoffs / total sims), (sims winning ship / total sims), etc...
- [ ] Display results on website
