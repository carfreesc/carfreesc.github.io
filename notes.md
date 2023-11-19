# Introduction

<div id = "map" style = "width: 400px; height: 200px">
<script>
   // Creating map options
   var mapOptions = {
   
	  center: [40.78570,-77.83720],
	  zoom: 15
   }

   // Creating a map object
   var map = new L.map('map', mapOptions);

   // Creating a Layer object
   var layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');

   // Adding layer to the map
   map.addLayer(layer);
      
   // Try adding a tag.
   var geojsonFeature = {
     "type": "Feature",
     "properties": {
        "name": "My house",
        "amenity": "Bathrooms",
        "popupContent": "We live here."
      },
      "geometry": {
        "type": "Point",
        "coordinates":  [40.78570,-77.83720]
      }
    };
   
   L.geoJSON(geojsonFeature).addTo(map);
</script>
</div>


A [2019 CityLab study](https://www.bloomberg.com/news/articles/2019-09-24/the-best-and-worst-u-s-places-to-live-car-free) ranked State College as the \#2 city in the nation for car-free living based on the very large number of car-free residents.  If you're moving here and anticipating a tranquil car-free existence, you're in for a rude awakening: what the study fails to mention is that nearly all of those car-free residents are undergraduates living in dormitories who seldom need to stray far from campus.  Living in State College without a car past the age of 22 is indeed possible, but it takes some dedication and planning.

I've tried to collect some practical advice and basic information about car-free commuting in the State College area, along with some editorialization.  The advice here is of course shaped by my own location, commute, tastes, fitness, budget,.. and won't apply to everyone.  There are many parts of town where I don't bike often, and I don't know the best streets.  I am often pulling a toddler in a trailer and may be more traffic-averse than you are.  Or less traffic-averse; my nerves are well-fried from a decade of big-city commuting.  If you'd like to share your own advice or correct mine you can make a pull request at, or just email carfreesc@gmail.com.

I don't claim to know much about car-free student life.  Certainly many students don't have cars, and you realistically won't need one unless you have a very far-off apartment or job.  If any student out there wants to write a bit about student life without a car let me know.  A similar offer applies to graduate students and postdocs.

# The basics

Although State College is relatively compact, it is not quite small enough that you can get away with walking everywhere.  In the absence of a car, you will need to rely on buses and biking (and maybe the occasional taxi/Uber).  Below is a map showing downtown, campus, and what are to my mind the "major" bike and bus routes.  The darker the color of a route, the more I like it.  Dark bus routes have regular and frequent service throughout the day, while light ones are designed for commuters and may have only morning and evening service.  Dark bike routes are separated off-road paths, and light ones or roads I like to ride (with or without bike lanes).  There are many other routes (bus and bike alike) not shown here; you should look at a map to see what's in your neighborhood.

There is a network of bicycle routes of various kinds.   There are a few nice off-road, fairly long distance routes that connect various parts of town over distances of a couple miles. Closer to downtown, bicycling infrastructure consists mostly of ritualistic paintings of bicycles on select streets ("sharrows"), with a couple painted bike lanes.  It is fairly well-established by now that sharrows have, if anything, a negative impact on bicycle safety, but this remains the heart of the borough's approach.  Do not be put off, however: State College's greatest bicycling asset is that it's just not that big and you can usually find a combination of quiet residental streets and the bike paths to take you where you need to go, sharrows or no.  We must be clear that it is cycling utopia: cyclists and pedestrians are seriously injured or killed with some regularity, and not much is done about it.  (Local politicians talk about supporting cycling, but to be honest I don't think I can name a significant cycling improvement in the borough since I was a kid 25 years ago. Maybe there is more momentum now; I'm not holding my breath.)

The Centre Region Council of Governments provides [an interactive bike map](https://centrecog.maps.arcgis.com/apps/webappviewer/index.html?id=b9264927503843b1a0c6836b50d99cc0) showing both off- and on-road options.  OpenStreetMaps has better coverage of local bike connections than Google maps.  (I don't know who is responsible, but thank you!)  OSM does not provide routing, but various third-party sites do.  I use [OpenRouteService](https://maps.openrouteservice.org/).  The suggestions are occasionally a little wonky, but so are Google's and at least OSM isn't tracking me.

Residential neighborhoods and developments can be found in many directions.  There are three ``historic'' neighborhoods that are easily walkable to campus: the Highlands (to the south), Holmes-Foster (to the west), and College Heights (to the north).  I suspect going car-free is easiest if you live in in one of these areas. But they are also more expensive and louder.  Park Forest is a large, mostly residential neighborhood northwest of downtown.  There is a good bike path to campus, but it may be a couple miles.  a variety of other neighborhoods also offer connections to convenient off-road bike paths, at the cost of being a little further away.

Much recent development has been along North Atherton Street, to the northwest side of town.  This (st)road is unfortunately a car-centric hellscape, and [$33,000,000 of recent "upgrades"](https://www.statecollege.com/atherton-street-project-cost-soars-past-estimate/)  have left it even more hostile to humans than it used to be. Your tax dollars at work.  It is often possible to reach destinations on N Atherton either by bus, or by biking in on a cross street through Park Forest, or by taking the Valley Vista path.

The bus network in town is [CATA](https://catabus.com/) (the Centre Area Transit Authority); the [Spring 2022 service map](http://catabus.com/wp-content/uploads/System-Map-Spring-2022.pdf) is here.  The buses are better than you would expect in a city of this size, but the schedules are still not always convenient depending on what you're trying to do.  All the routes are to/from campus or downtown, so if you're trying to get somewhere else you will probably need a (lengthy) connection.

There are two main types of routes: some "circulator" routes with fairly direct and relatively frequent service, and some "commuter" lines that go from a particular neighborhood to downtown or campus, but tend to be pretty slow since they take indirect routes.  A few of the routes downtown or on campus are subsidized and don't cost anything; for most of the others you'll need tokens, which cost a couple bucks each.



# Bike routes

## Off-road

* The **Orchard Park** bike path runs from near the high school out to the southwest side of town (Cato Park, Harner Farm, YMCA,...).  It has an easy connection to downtown and campus via Gill St.

* Several paths go through and around the PSU **golf courses**.  A north/south route along the old Corl St connects the western edge of downtown to the Tudek/Circleville and Blue Course paths.  Another path follows College Avenue  most of the way from campus to Blue Course, with connections possible to Gill St and others.  To the east one has access to campus, including through the IST bridge to Pollock Rd.

* The **South Atherton** bike path goes from around Atherton/University out to Boalsburg, about five miles.  It connects to downtown via a cut-through to Garner St.  It is not the best path, crossing a lot of turn-offs for businesses and featuring a couple rather violent curb cuts, but it's the best option in this direction. You will see the more hardcore cyclists riding on the road instead, but not me.  The crossing signal at Rolling Ridge has been removed for months and a no pedestrian signs has been put up in its place.   Maybe we are not supposed to use the path anymore?  Baffling.

* The **Blue Course** bike path follows Blue Course Dr, from Radio Park elementary, skirting the western edge of the golf course, and ending near Orchard Park.

* The **Tudek/Circleville** bikeway runs from Tudek Park and Radio Park west to Valley Vista (and a bit beyond, with access to the Scotia gamelands off Sleepy Hollow).  At the eastern end, it has easy connections to both the golf course paths (leading to campus and downtown) and the blue course path.  At the western end, it connects to the Valley Vista multi-use path, which provides a route north towards Grays Woods.

* There are two parallel north/south paths on the western side of town, one along **Valley Vista** and one on **Circleville**.   The path on Valley Vista connects to the Tudek path and the rest of the network at the intersection with Science Park. The Circleville Park begins further north but reaches all the way to Grays Woods. You can get from Valley Vista to the Circleville path by cutting through Circleville Park; take the turn-off for "Little Lion Drive" which is Park Forest Middle School.  Together, these paths will get you from downtown all the way to Grays Woods with virtually no riding on a road.  It's about seven or eight miles.

## Roads

The most difficult place to navigate on a bike is downtown, where there are few bike lanes and more traffic. I've color-coded this map according to how much I like various streets.

Let me opine on a few specific roads.

* **Foster Avenue** is just a block up from Beaver Ave and is my go-to route for getting places in town: take Foster to the correct cross street and then head in. (Yes, I live south of downtown.) It is a designated bike route for (almost) its entire length, although there is no bike lane except for one small stretch.  However, it is not a through street for cars, which are blocked by Central Parklet and an island in Atherton St.  It is usually pretty quiet traffic-wise, although party-wise it gets a little rowdy on the weekends through frat row.  For some reason Google Maps is not aware that you can bike Foster end-to-end so it spits out some weird routes; ignore it.

The worst crossing on this route is at Atherton, which does not have a light but does have a pedestrian island in the middle.  There also is some kind of sign suspended over the road suggesting that cars might consider yielding to pedestrians.  Having made this crossing afoot or apedal several thousand times since the installation of the sign, I can say with some confidence that it has no impact on driver behavior whatsoever; you can stand in the middle of the road in a thunderstorm and still watch a dozen cars go by.  Nevertheless the planning commission is considering dropping $60k of precious transit money installing another one of these gadgets at Fairmount, another dangerous and popular crossing in need of actual improvement.

* **Calder Way** is an alley between Beaver and College with a lot less traffic than either.  However, many businesses receive their deliveries there and riding can still be a little dicey.  It is also one-way through much of downtown.  I think there have been some rumblings in borough council about bike and pedestrian improvements to Calder, which would be great, but I am not plugged-in enough to know what (if anything) is actually going to happen.  For now, it's a fine option if you just want to go a couple blocks downtown.

* Most cross streets to Beaver and College in the downtown area are basically fine to ride on.  Some I find especially convenient depending on how far west I am and which one-ways are the right way are **Gill**, **Garner**, **Allen**, **Hetzel**, and **Locust**.  The big roads to avoid are **Atherton** and **University**.  On the west side, **Buckhout** is bad between College and Beaver.

* **Allen St** is a conundrum.  On the downtown side of Foster, it has no bike lane, but I ride it all the time.  Just take the whole lane if you need to.  On the out-of-town side of Foster, it has a bike lane, but I avoid it: cars often blast down the hill and there's a weird intersection at McCormick.  I find Pugh a block over to be a bit more peaceful.

* **Garner** is my usual route from downtown to parts south.  There is a bike lane most of the way, although unfortunately coming into town you are unceremoniously dumped into the slightly treacherous intersection with Beaver.  Be careful: if continuing straight towards College you have to cross traffic and get in the middle lane as you approach the intersection, since a right turn lane appears.  Not infrequently the cars in the right turn lane go straight anyway, so you may need to swap places with them again as the road narrows back to one lane.   It's a tricky stretch, so surely the planners at least painted the bike lane to indicate where the paths of traffic cross?  Nope! In the face of difficulty, they simply threw up their hands: the bike lane evaporates completely and there are not even sharrows on that stretch.  You'll still find it marked as a bike route on the CRCOG map, though. (If you want to play it safe, make the Foster -> College cut a block over on Hetzel instead.)

Headed south, you should resist the temptation to bomb down the hill to Easterly since a) there is a stop sign at the bottom and b) cars tend thorough to roll the stop signs at the crosses; I usually take the middle of lane.  Note that at end the of the bike lane you can cut through to the path on S Atherton after a small bit of sidewalk.

* **Sparks** is a designated bike route for some reason and has some sharrows, with bike lanes on a couple random blocks, only ever on one side of the street at a time.  It's the busiest north/south street in this vicinity since it connects College to Westerly.  There is no reason to ride here unless it's your destination; go a block over to Gill, which also connects College to Westerly, but not for cars.  (I guess the one advantage is that it does buy you a light across Beaver.)

* **Easterly/Westerly Parkway** is designated as a bicycle route on the COG map.  Again they did slap down some sharrows, but it's a narrow, curving road with a not unfast traffic and not much of a shoulder.  That is nothing about it deserving of a bicycle designation, but there is not any good alternative.   There is now  [$1.1 million funding](https://www.statecollege.com/three-centre-county-transportation-alternatives-projects-receive-more-than-2-million-in-funding/) for an off-road multi-use path along Westerly, so this should improve in the next few years.  (Don't let this lift your spirits too much; in comparison, the borough will soon blow $2.55 million(!) on a totally unneeded new surface lot(!) on Nittany.)

## Campus

There are relatively few roads on campus, but most of them are fine to ride on.  In areas without roads, biking on the sidewalks is permitted as long as you ride like a sane person and yield to pedestrians.  As in all things, there is an official PSU policy with the details: [SY16 Regulations for Bicycles / Skateboards / Scooters / In-Line Skates / Roller Skates / Electric Personal Assistive Mobility Devices](https://policy.psu.edu/policies/sy16).

* **Pollock** cuts east-west across campus (this is the road in front of the HUB).  It has no bike lane, but gates in the middle mean it is closed to cars for most of the day (except for OPP and bigwigs with a permit to park at Old Main).  It also connects to the IST building, a (walk-your-)bikable bridge over Atherton.

* **Curtin** is another east-west street, but a lot busier.  It's basically rideable, but prefer Pollock when you can.

* **Shortlidge** is the extension of Garner onto campus.  It has a bike lane and is a fine option to go north/south or connect back into town.


# Biking considerations

## Facilities

There are two bicycle shops in town: **Freeze Thaw Cycles** downtown near College & Allen, and **The Bicycle Shop** a few blocks to the west at Beaver and Barnard.  Both are excellent, but can also have very long waits, especially during peak seasons.   These are not the only options for repairs.  **Blacklist Bicycles** is a mobile repair shop, who I gather will show up at your house with a van and fix your bikes.  **The Bike Den** is located in a PSU parking garage on the west end of campus and has a variety of tools and classes available.
There are also a lot of little "bike repair stations" around, in case you just need an Allen Wrench or a pump. (PS: Does anybody actually use these things?  They have always struck me as a useless way for the powers that be to appear to be doing something pro-bike, or maybe to check a box to get that prized silver-medal designation.  But I would be happy to be wrong.)

You are supposed to register your bicycle and put on a little sticker on the frame; you can do it at any of the bike shops or online.  I think in theory you could be fined if you don't, but mostly it helps the police track the bike if it's stolen.  Speaking of which, a good bike lock is essential.

## Terrain

State College is fairly hilly.  If you don't think you'll be able to make it up the hills, you might consider an eBike, or using the "Spin" eBike sharing program that's available in many parts of town.

If you're ever feeling nervous about traffic, you usually have the option of riding on the sidewalk.  In the borough, sidewalk riding is allowed everywhere except the "downtown business district", defined in ordinances as the area shaded below.  On campus, sidewalk riding is allowed outside the "Bicycle Exclusion Zone", which is bounded by Curtin to the north and Pollock to the south.  You can also just walk your bike on the sidewalk.


### Seasonal issues

It can get pretty cold here in the winter.  If you're commuting in the morning, you are looking at a couple months below freezing, and sometimes a day or two a year where the temperature dips below 0 F.  You'll want to dress appropriately.  I am a convert to [Bar Mitts](https://barmitts.com/).  I know they have them at Freeze Thaw.

Snow is typically cleared pretty quickly and the roads are salted to the point that they are fine to bike on, but you'll probably want to take extra care to avoid ice and traffic after a storm.
Most of the major off-road paths are theoretically cleared in the winter.  The exceptions I am aware of are in the golf course (both the gravel path parallel to college, anjd the remains of Corl St) and the path along 322 from Scenery Park towards Lemont. A short stretch of the connection from the S Atherton bike path to Garner runs along private sidewalks, and these have not reliably been cleared the last couple years.
In my experience the other paths are  cleared pretty quickly, but people who actually commute on them might have better information.  I did have a couple very icy trips on S Atherton in 2022.  Sidewalks and roads on campus are reliably cleared early and quickly.

It gets dark early in the winter.  It will be totally dark by the time of the 5 o'clock trip home.  Good bike lights, front and back, are called for, both by the law and by common sense.

On football weekends, Arts Fest, and the first couple weeks of every semester, State College is flooded with tourists and students who don't know the roads.  Expect all manner of crazy driving: wrong-way drivers, drivers speeding down unsigned alleys and blowing across real streets, etc.

# Other transportation

## Rental bikes

There is a network of shared eBikes available for rent all over town and campus, Spin bikes.  I have never ridden one, but the service seems to be very popular and I see the bikes all over the place.  I do not know exactly what area has reliable coverage.

## Car rental

It is probably unavoidable: sometimes you need a car.  There are several car rental options not too remote from downtown.  If you're a PSU employee, you can get outstanding deals on personal car rentals through [National and Enterprise using the Big Ten discount](https://pennstateoffice365.sharepoint.com/sites/NationalEnterpriseCarRentalAgreement) (at time of writing, the base rate is about $200/wk).  They have a rental office at College and Blue Course which is a couple miles walking or can be reached by several bus lines from downtown.  Note: you can rent a car for quite a few week(ends)s per year before you would save money by owning one.

Zipcar and the Enterprise carshare in town both appear to be defunct and I am not aware of any alternative carshare.

## Amtrak

State College does not have direct train service on Amtrak.  The closest stations are in Lewistown and Tyrone, which are both about 35 minutes from here, but in opposite directions.  If you're traveling west (to Pittsburgh and beyond), it usually makes sense to catch the train in Tyrone.  If you're traveling east (Harrisburg or Philadelphia), you can catch the train in Lewistown.  Both of these are served by the Amtrak *Pennsylvanian* route and have just a single train per day each direction; this is expected to go up to two trains daily within the next couple years, [thanks to the 2022 infrastructure bill](https://www.post-gazette.com/news/transportation/2022/06/27/penndot-norfolk-southern-reach-deal-expand-train-service-pittsburgh-harrisburg-western-pennsylvania/stories/202206270059).

You can also buy a ticket directly from State College on amtrak.com.  These tickets involve a "Thru-Way" bus: you board a bus downtown and then transfer to a train, usually about 90 minutes away in Harrisburg.  Harrisburg has frequent train service (Amtrak owns the track from there to Philly) and the bus-train transfer is inside the same building, so this tends to be pretty convenient.  Recent cuts to bus service have greatly reduced the number of schedules available, but it's still worth checking.

## Taxi

Local taxi service unfortunately took a big hit during the pandemic.  The only company still standing is Nittany Express, and they only have a couple cars running at any given time.  I don't do Uber/Lyft/... but my impression is that they are viable options.

## Airport

The local airport is University Park (SCE), located about five miles north of town.  Although it is a scenic bike ride to get there, this is not very practical with luggage.  There is no bus service: you will need to get a taxi or a ride.  Nittany Express will let you reserve an airport shuttle, but you need to book ahead.


# Specific Destinations

## Groceries and Markets

Grocery shopping presents a bit of a challenge: the bus service is oriented around getting passengers to/from downtown, but there is no supermarket there.  If you're hoping to shop by bus the schedules and connections are likely to be challenging unless you happen to live a short walk from one of the stores.

My own strategy is to make only infrequent trips to the supermarket (every three or four weeks) and get fresh items and small shops more often elsewhere.  Your mileage may vary.  There are a variety of grocery options in town.

* **McLanahan's** is a smaller grocery store right downtown at Beaver and Allen.  Locals may perceive it as a student grocery store and never set foot there.  Don't make this mistake!  It has a nice if somewhat small selection of groceries and is a great place to pick up a couple items without a full shopping trip.
* **Target** has a smaller store in town with many useful things that will save you a trip to the land of big boxes out N Atherton.
* **The Cheese Shoppe** sells cheeses and coffee.  They have better cheese than any of the supermarkets.
* **Gemelli** bakery has good bread.
* **Way Fruit Farm** from Stormstown has a new farm store and cafe.  Recommended.
* **International Market** on Allen has a pretty wide array of international products.

If you are a car-free enthusiast of local foods, do not despair; there are several ways to get local produce without driving.  Sometimes you have to eat a delivery fee; at these times, it may help to reflect on how much money you are saving by not having a car.

* The **Downtown Farmers Market** happens on Locust Lane every Friday spring through fall. In the late summer, it runs on Tuesday as well.  (There also used to be a winter market in the borough building but it seems to have ended with COVID.)  Unfortunately the last few years the further-away markets have grown bigger than the downtown one: there is a large market in Boalsburg on Tuesdays (five easy miles out the South Atherton path, but the bumps are a bit rough on fruit) and one on North Atherton on Saturdays (probably doable on the Valley Vista path, but again with the bumps).  

* [**Centre Markets**](https://www.centremarkets.com/) lets you place an order ahead of the farmers market and have it delivered.  They have a wide range of produce and meat, as well as prepared foods from local vendors. You can also combine your order with an order from Nature's pantry, a  natural foods store out E College that is not a great ride but is now accessible via the College Ave circulator)

* **Way Fruit Farm** operates a farm store downtown.

* Several **CSAs** offer weekly delivery of boxes of produce and dairy that help reduce the number of grocery trips you need; I use and recommend [GroundWork Farms](https://www.centremarkets.com/).

* **Vale Woods Farm** offers delivery of milk and other dairy products.

* **Mark's Custom Meats** in Howard delivers to State College a couple times a week.

There are some grocery stores with easy bike access.  You would be surprised how much you can fit in a bike trailer or even panniers.

* **Weis Markets** is located on Westerly right next to the high school.  It is accessible via the Orchard Park bike path.

* **Weis** and **Giant** both have stores in Hills Plaza, off the South Atherton bike path.

* **Wegman's**, **Trader Joe's**, and **Weis** all have locations in the vicinity of North Atherton.  It is possible to access all of these through Park Forest or using the Atherton Connector.

## Medical

Doctors and dentists are spread throughout town.  There are a few concentrations of medical offices.

* The hospital in town is **Mount Nittany Medical Center**.  It's a couple miles bike ride, some of it on Park Avenue and fairly unpleasant. CATA service to the hospital was recently discontinued; the Penn State Campus shuttle now stops there during business hours and may be the only option.

* Geisinger Healthplex State College (a.k.a. **Geisinger Grays Woods**) is located in the Grays Woods development off I-99 a bit to the northwest of downtown.   Fairly frequent bus service is available on the W route.  Although it is a bit far, it is easily bikable via the Tudek/Circleville + Valley Vista + Circleville paths with only a short stretch on Scotia Rd at the end.

* **Scenery Park** has a variety of medical facilities.  There is easy access via the South Atherton bike path.

There are doctors and dentists in many other places too.  Mount Nittany has some primary care doctors at a facility on Blue Course, which has good bike access.  There are optometrists and dentists downtown and in Scenery Park.

## Entertainment

* One of the great advantages of living in State College is our proximity to the woods.  Unfortunately, your options are somewhat limited if you need to bus/bike to the trailhead.  There are various connections to the Scotia gamelands, e.g. at the western terminus of the Tudek/Circleville path on Sleepy Hollow Rd.  Easy places to get in (which are also busier) are Musser Gap and Shingletown Gap.  (There are of course many other beautiful places to bike, but the bike part starts to become the trip instead of just the transit.)

* The **State College Spikes** play at Lubrano Park, which is easy to reach by various bus routes (e.g. the Red Link), or by biking through campus.

* **Penn State football** plays at Beaver Stadium.  I stay as far as possible away from the stadium on game days and have no advice to offer.

## Miscellany

* The easiest hardware store to get to is **Ace Hardware** in Hills Plaza off South Atherton.  Lowe's and Home Depot are reachable via the Valley Vista path or the W bus.

* **Meyer Dairy** on South Atherton is a local landmark.  It is not easy to reach despite being across from the bike path: I think the easiest route is to take Rolling Ridge north, ride through the KBB parking lot, and then jump a curb and cross a little grass to get to the dairy.

* The **DMV** is located in Pleasant Gap, about eight miles out of town.  There is no longer bus service, but there is (for the time being) service on CATAGO.  Even this may end with Spring Township withdrawing from CATA.  It is possible to bike, but the road is deeply unpleasant as you get closer to State College. You also have to ride through the grounds of the Rockview state prison; I have done this a handful of times and never saw any signage that it's not allowed, but I wouldn't swear that it is.  For this one, I recommend driving.

# Other resources

I am not a serious road or mountain cyclist and can't tell you much about non-commuter aspects of the local cycling scene.  Here are some links:

* **CentreBike** is the main local advocacy group.

* **NMBA** is the mountain bikers.

* **Organized rides** take place all the time.

* **Bellefonte** is the closest other really separate city.  You can take a bus.

* The **State College Borough Council** is responsible for much of this mess and you should attend their meetings and complain.

* Other nearby cities are difficult to reach without a car. CATA organizes commuter carpools to some.

