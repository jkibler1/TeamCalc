# Pokemon Battle Tree Team Type Synergy Calculator GUI with Kivy
# Input a single pokemon type combo and get best possible 2 ally pokemon with fewest weaknesses and un-resists.
# v1.1  Add sorting.
#       Combine GUI and original design scripts.

__author__ = "Josh Kibler"
__version__ = "1.1"
__status__ = "dev"
__date__ = "3.8.2021"

import copy, re, kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, ObjectProperty, ColorProperty
from kivy.uix.button import Button
#from kivy.event import EventDispatcher

# Global variables

typeMUs = {"normal": {2:["fighting"],.5:[],0:["ghost"]},
         "fire": {2:["water","ground","rock"],.5:["fire","grass","ice","bug","steel","fairy"],0:[]},
         "water": {2:["electric","grass"],.5:["fire","water","ice","steel"],0:[]},
         "electric": {2:["ground"],.5:["electric","flying","steel"],0:[]},
         "grass": {2:["fire","ice","poison","flying","bug"],.5:["water","electric","grass","ground"],0:[]},
         "ice": {2:["fire","fighting","rock","steel"],.5:["ice"],0:[]},
         "fighting": {2:["flying","psychic","fairy"],.5:["bug","rock","dark"],0:[]},
         "poison": {2:["ground","psychic"],.5:["grass","fighting","poison","bug","fairy"],0:[]},
         "ground": {2:["water","grass","ice"],.5:["poison","rock"],0:["electric"]},
         "flying": {2:["electric","ice","rock"],.5:["grass","fighting","bug"],0:["ground"]},
         "psychic": {2:["bug","ghost","dark"],.5:["fighting","psychic"],0:[]},
         "bug": {2:["fire","flying","rock"],.5:["grass","fighting","ground"],0:[]},
         "rock": {2:["water","grass","fighting","ground","steel"],.5:["normal","fire","poison","flying"],0:[]},
         "ghost": {2:["ghost","dark"],.5:["poison","bug"],0:["normal","fighting"]},
         "dragon": {2:["ice","dragon","fairy"],.5:["fire","water","electric","grass"],0:[]},
         "dark": {2:["fighting","bug","fairy"],.5:["ghost","dark"],0:["psychic"]},
         "steel": {2:["fire","fighting","ground"],.5:["normal","grass","ice","flying","psychic","bug","rock","dragon","steel","fairy"],0:["poison"]},
         "fairy": {2:["poison","steel"],.5:["fighting","bug","dark"],0:["dragon"]}}
typecolors = {"none": '#000000',
         "normal": '#aaaa99',
         "fire": '#ff4422',
         "water": '#339999',
         "electric": '#ffcc33',
         "grass": '#77cc55',
         "ice": '#66ccff',
         "fighting": '#bb5644',
         "poison": '#aa5599',
         "ground": '#ddbb55',
         "flying": '#889aff',
         "psychic": '#ff5599',
         "bug": '#a9bb22',
         "rock": '#bbaa66',
         "ghost": '#454582',
         "dragon": '#7866ee',
         "dark": '#775544',
         "steel": '#aaaabb',
         "fairy": '#ee99ee'}
allTypeMUs = copy.deepcopy(typeMUs)
allTypeMUs_simp = copy.deepcopy(typeMUs)
# testdict = {'grass steel/steel fairy': {'rating': 10.50, 'tweaks': ['fire', 'water', 'ice'], 'tURs': ['fire']},
#             'water ground/steel fairy': {'rating': 10.25, 'tweaks': ['normal', 'bug'], 'tURs': []}}

# Team -----------------------------------------------------------------------------------------------------------------
class Team:
    def __init__(self, pkmn1, pkmn2, pkmn3):
        self.pkmn1 = pkmn1
        self.pkmn2 = pkmn2
        self.pkmn3 = pkmn3
        #self.teamEffectsUnsorted = {}
        self.teamEffects = {}
        self.teamRating = 0
        self.teamTypes = pkmn1.types + "/" + pkmn2.types + "/" + pkmn3.types
        self.teamTypes_simp = pkmn2.types + "/" + pkmn3.types
        self.weaksNum = 0
        self.weaksList = []
        self.resistsList = []
        self.URList = []

    # get effects (strengths and weaknesses) of pokemon team type combo
    # accept boolean whether simplified or unsimplified effects wanted?
    def getTeamEffects(self):
        #pkmn1Effects = self.pkmn1.effects
        #pkmn2Effects = self.pkmn2.effects
        #print(pkmn1Effects)
        #print(pkmn2Effects)
        # merge effect list values in all 3 type dicts (could also try using .format and replace variable name w/loop)
        if self.pkmn1.types in allTypeMUs_simp:
            types1dict = copy.deepcopy(allTypeMUs_simp[self.pkmn1.types])
        else:
            types1dict = copy.deepcopy(allTypeMUs_simp[self.pkmn1.typesR])
        if self.pkmn2.types in allTypeMUs_simp:
            types2dict = copy.deepcopy(allTypeMUs_simp[self.pkmn2.types])
        else:
            types2dict = copy.deepcopy(allTypeMUs_simp[self.pkmn2.typesR])
        if self.pkmn3.types in allTypeMUs_simp:
            types3dict = copy.deepcopy(allTypeMUs_simp[self.pkmn3.types])
        else:
            types3dict = copy.deepcopy(allTypeMUs_simp[self.pkmn3.typesR])
        merged = {4:[],2:[],1:[],0.5:[],0.25:[],0:[]}
        #print(types1dict)
        #print(types2dict)
        # for each effect key in merged
        for key in merged:
            # append from all 3 pkmn types dicts to same effect key in merged dict
            if key in types1dict:
                for value in types1dict[key]:
                    #print(value)
                    #print(merged[key])
                    merged[key].append(value)
            if key in types2dict:
                for value in types2dict[key]:
                    # print(value)
                    # print(merged[key])
                    merged[key].append(value)
            if key in types3dict:
                for value in types3dict[key]:
                    # print(value)
                    # print(merged[key])
                    merged[key].append(value)
            #print(merged)

        # find effect of type in all 3 dicts, multiply together then form new dict based on results
        for type in typeMUs:
            multlist = []
            #print(type)
            # for each effect key in merged
            for key in merged:
                count = merged[key].count(type)
                if count > 0:
                    multlist.append(key**count)
                    # must get resists before multiplication
                    if key < 1 and type not in self.resistsList:
                        # print(key,type,self.URList)
                        self.resistsList.append(type)
            # if self.teamTypes == 'fire dragon/flying/normal steel':
            #     print(type, key, merged[key].count(type), key**count)
            #print(merged)
            result = 1
            for x in multlist:
                result = result * x
            # if self.teamTypes == 'fire dragon/flying/normal steel':
            #     print(multlist, result)
            # add effect to corresponding list in teamEffects dict
            self.teamEffects.setdefault(result, []).append(type)

        # get unresists based on types absent from resists list
        for type in typeMUs:
            if type not in self.resistsList:
                self.URList.append(type)

        # sort effects from high to low
        # sort = sorted(self.teamEffectsUnsorted.items(), reverse=True)
        # for e in sort:
        #     self.teamEffects[e] = sort[e]
        return sorted(self.teamEffects.items(), reverse=True)
        #return self.teamEffects

    # get rating of pokemon team type combo
    def getTeamRating(self):
        # get effect number for each type
        for type in typeMUs:
            typeEffectFound = False
            # while typeEffectFound:
            # for each effect number list
            for effect in self.teamEffects:
                # if type in effect number list
                if type in self.teamEffects[effect]:
                    #print(type, effect)
                    self.teamRating += effect
                    typeEffectFound = True
                    break
            if typeEffectFound == False:
                # print(type)
                # print(1)
                self.teamRating += 1
        return self.teamRating

    # get number of team weaknesses
    def getWeaks(self):
        # if no weaknesses
        if max(self.teamEffects) < 2:
            self.weaksNum = 0
            #self.weaksList.append('none')
        # if weaknesses
        else: #if max(self.teamEffects) > 1:
            #print(self.teamTypes)
            for key in self.teamEffects:
                if key > 1:
                    self.weaksNum += len(self.teamEffects[key]) * key/2
                    if key == 4:
                        for weak in self.teamEffects[key]:
                            self.weaksList.append(weak + "X2")
                    elif key == 8:
                        for weak in self.teamEffects[key]:
                            self.weaksList.append(weak + "X4")
                    else:
                        for weak in self.teamEffects[key]:
                            self.weaksList.append(weak)
        return self.weaksList

# Pokemon --------------------------------------------------------------------------------------------------------------
class Pokemon:
    #type 2 optional, blank by default
    def __init__(self,type1,type2=""):
        self.type1 = type1
        self.type2 = type2
        if type2 != "":
            self.types = type1 + " " + type2
        else:
            self.types = type1
        self.typesR = type2 + " " + type1
        #self.effectsUnsorted = {}
        self.effects = {}
        self.effectsSimp = {}
        self.rating = 0
    # get effects (strengths and weaknesses) of pokemon type combo
    def getEffects(self):
        # merge effect list values in both type dicts (if 2 types)
        if self.type2 != "":
            typesChecked = []
            type1dict = copy.deepcopy(typeMUs[self.type1])
            type2dict = copy.deepcopy(typeMUs[self.type2])
            merged = type1dict
            #for each effect key in type2 dict
            for key in type2dict:
                #append type to same effect key in merged dict
                for value in type2dict[key]:
                    merged[key].append(value)
            #for each key in merged dict
            for key in merged:
                for value in merged[key]:
                    multlist = []
                    #make sure type not checked already
                    if value not in typesChecked:
                        typesChecked.append(value)
                        for key2 in merged:
                            for value2 in merged[key2]:
                                #where type match, append to list to multiply
                                if value == value2:
                                    multlist.append(key2)
                        result = 1
                        for x in multlist:
                            result = result * x
                        #add effect to corresponding list in effects dict
                        self.effects.setdefault(result, []).append(value)
        else:
            self.effects = typeMUs[self.type1]
        # sort effects from high to low
        #sort = sorted(self.effectsUnsorted.items(), reverse=True)
        #self.effects = collections.OrderedDict(sort)
        # for e in sort:
        #     #print(e[0])
        #     ekey = e[0]
        #     self.effects[e] = sort[ekey]
        return self.effects

    # get simplified effects (without quad strengths and weaknesses) of pokemon type combo
    def getEffectsSimp(self):
        self.effectsSimp = copy.deepcopy(self.effects)
        if 4 in self.effectsSimp:
            if 2 not in self.effectsSimp:
                self.effectsSimp[2] = []
            for e in self.effectsSimp[4]:
                self.effectsSimp[2].append(e)
            self.effectsSimp.pop(4)
        if 0.25 in self.effectsSimp:
            if 0.5 not in self.effectsSimp:
                self.effectsSimp[0.5] = []
            for e in self.effectsSimp[0.25]:
                self.effectsSimp[0.5].append(e)
            self.effectsSimp.pop(0.25)
        if 0 in self.effectsSimp:
            if 0.5 not in self.effectsSimp:
                self.effectsSimp[0.5] = []
            for e in self.effectsSimp[0]:
                self.effectsSimp[0.5].append(e)
            self.effectsSimp.pop(0)
        return self.effectsSimp

    # get rating of pokemon type combo
    def getRating(self):
        # get effect number for each type
        for type in typeMUs:
            typeEffectFound = False
            #while typeEffectFound:
            # for each effect number list
            for effect in self.effects:
                # if type in effect number list
                if type in self.effects[effect]:
                    #print(type, effect)
                    self.rating += effect
                    typeEffectFound = True
                    break
            if typeEffectFound == False:
                # print(type)
                # print(1)
                self.rating += 1
        return self.rating

# Global functions -----------------------------------------------------------------------------------------------------
def intitialize():
    # first correct all single types to simplified effects
    for key in allTypeMUs_simp:
        split = key.split()
        if len(split) == 2:
            pkmn = Pokemon(split[0], split[1])
        else:
            pkmn = Pokemon(split[0])
        allTypeMUs_simp[key] = pkmn.getEffects()
        allTypeMUs_simp[key] = pkmn.getEffectsSimp()

    # iterate all possible type combos to generate all their effects
    for key in typeMUs:
        for key2 in typeMUs:
            # do not generate same type combos (e.g. normal normal)
            if key != key2:
                pkmn = Pokemon(key, key2)
                # do not generate already generated combos in opposite order (e.g. normal water, water normal)
                if pkmn.typesR not in allTypeMUs:
                    allTypeMUs[pkmn.types] = pkmn.getEffects()
                    allTypeMUs_simp[pkmn.types] = pkmn.getEffectsSimp()

def calculate(pkmntype1, pkmntype2):
    # global variables
    global rsort1,rsort2,psort1,psort2,wsort1,wsort2,usort1,usort2,noWeakTeamsNum,oneWeakTeamsNum,teamsDict2
    rsort1 = {}
    rsort2 = {}
    psort1 = {}
    psort2 = {}
    wsort1 = {}
    wsort2 = {}
    usort1 = {}
    usort2 = {}

    # reset variables
    teamsDict = {}
    teamsDict2 = {}
    noWeakTeamsNum = 0
    oneWeakTeamsNum = 0
    ratingMin = 100
    ratingMax = 0
    tfilter = '-'
    writable = True

    pkmn1 = Pokemon(pkmntype1, pkmntype2)

    #pkmn1.getEffects()
    lookupEffects(pkmn1, allTypeMUs)
    #pkmn1.getEffectsSimp()
    lookupEffects(pkmn1, allTypeMUs_simp)
    pkmn1.getRating()

    # iterate over all type MUs SIMPLIFIED to get effects
    for key in allTypeMUs_simp:
        if key != pkmn1.types and key != pkmn1.typesR:
            # print(key)
            split = key.split()
            if len(split) == 2:
                pkmn2 = Pokemon(split[0], split[1])
            else:
                pkmn2 = Pokemon(split[0])
            # Look up effectiveness from dict
            lookupEffects(pkmn2, allTypeMUs_simp)
            # print(pkmn2.effects)

            # loop for 3rd pokemon
            for key2 in allTypeMUs_simp:
                # print(key2, pkmn2.types)
                if key2 != key and key2 != pkmn1.types:
                    # print(key)
                    split = key2.split()
                    if len(split) == 2:
                        pkmn3 = Pokemon(split[0], split[1])
                    else:
                        pkmn3 = Pokemon(split[0])
                    # Look up effectiveness from dict
                    lookupEffects(pkmn3, allTypeMUs_simp)
                    #print(pkmn3.effects)

                    team = Team(pkmn1, pkmn2, pkmn3)
                    teamR = Team(pkmn1, pkmn3, pkmn2)

                    # Build teams dict data output (only when team types reversed not already in to prevent dupes)
                    if teamR.teamTypes not in teamsDict:
                        team.getTeamEffects()  # MUST run before getTeamRating()
                        teamsDict[team.teamTypes] = {'rating': team.getTeamRating(), 'tweaks': team.getWeaks(), 'tURs': team.URList}
                        if team.teamRating < ratingMin:
                            ratingMin = team.teamRating
                        if team.teamRating > ratingMax:
                            ratingMax = team.teamRating
                        if team.weaksNum == 0:
                            noWeakTeamsNum+=1
                        elif team.weaksNum == 1:
                            oneWeakTeamsNum+=1
            #print(noWeakTeamsNum,oneWeakTeamsNum)

    topPercent = (ratingMax - ratingMin)/10 + ratingMin
    print("Top 10% rating threshold: " + str(topPercent))
    # Correct teamsDict key names to exclude first pokemon types after calc, and filter top 10%/all 0/1 weak teams
    # and add to full data to file
    try:
        file = open("teams_output.csv", "w")
    except:
        print('Warning: unable to export output to file.')
        writable = False
    for key,value in teamsDict.items():
        if(writable):
            rating = str(value['rating'])
            team = re.sub(" ", "_", key)
            tweaksnum = str(len(value['tweaks'])) + ":"
            tweaks = re.sub(" ", "_", str(value['tweaks']))
            tweaks = re.sub("[\[',\]]", "", tweaks)
            tURsnum = str(len(value['tURs'])) + ":"
            tURs = re.sub(" ", "_", str(value['tURs']))
            tURs = re.sub("[\[',\]]", "", tURs)
            file.write(rating + "\t" + team + "\t" + tweaksnum + tweaks + "\t" + tURsnum + tURs + "\n")

        split = key.split('/')
        new_key = split[1] + '/' + split[2]
        #print(key, split, new_key)
        #teamsDict2[new_key] = value
        #print(new_key,value)

        if value['rating'] <= topPercent and len(value['tweaks']) < 3:
            teamsDict2[new_key] = value
        elif len(value['tweaks']) == 0:
            teamsDict2[new_key] = value
        elif len(value['tweaks']) == 1:
            if 'X' not in value['tweaks'][0]:
                teamsDict2[new_key] = value
    if(writable):
        file.close()
    # print(rsort1)

    # teamsDict2 = {'grass steel/steel fairy': {'rating': 10.50, 'tweaks': ['fire', 'water', 'ice'], 'tURs': ['fire']},
    #           'water ground/steel fairy': {'rating': 10.25, 'tweaks': ['normal', 'bug'], 'tURs': []}}

    # Get different sorts by field
    rsort1 = sorted(teamsDict2.items(), key=lambda x: x[1]['rating'])
    rsort2 = sorted(teamsDict2.items(), key=lambda x: x[1]['rating'], reverse=True)
    # psort1 = sorted(teamsDict2.items(), key=lambda x: x[0])
    # psort2 = sorted(teamsDict2.items(), key=lambda x: x[0], reverse=True)
    wsort1 = sorted(teamsDict2.items(), key=lambda x: len(x[1]['tweaks']))
    wsort2 = sorted(teamsDict2.items(), key=lambda x: len(x[1]['tweaks']), reverse=True)
    usort1 = sorted(teamsDict2.items(), key=lambda x: len(x[1]['tURs']))
    usort2 = sorted(teamsDict2.items(), key=lambda x: len(x[1]['tURs']), reverse=True)

    # export full teams data to file
    # try:
    #     with open("teams_output.csv", "w") as file:
    #         # Output sorted data
    #         i = 0
    #         while i < len(rsort1):
    #             #print(str(team))
    #             rating = str(rsort1[i][1]['rating'])
    #             team = re.sub(" ", "_", str(rsort1[i][0]))
    #             tweaksnum = str(len(rsort1[i][1]['tweaks'])) + ":"
    #             tweaks = re.sub(" ", "_", str(rsort1[i][1]['tweaks']))
    #             tweaks = re.sub("[\[',\]]", "", tweaks)
    #             tURsnum = str(len(rsort1[i][1]['tURs'])) + ":"
    #             tURs = re.sub(" ", "_", str(rsort1[i][1]['tURs']))
    #             tURs = re.sub("[\[',\]]", "", tURs)
    #             file.write(rating + " " + team + " " + tweaksnum + tweaks + " " + tURsnum + tURs + "\n")
    #             # tsv file output (simpler but maybe less programs can read)
    #             # file.write(str(rsort1[i][1]['rating']) + "\t" + str(rsort1[i][0]) + "\t" + str(rsort1[i][1]['tweaks']) + "\t" + str(rsort1[i][1]['tURs']) + "\n")
    #             i += 1
    # except:
    #     print('Warning: unable to export output to file.')
    #     return
    # print('Teams from best to worst rating output to file "teams_output.csv".')
        # for team in rsort1:
        #     #strip = str(team).strip()
        #     print(team[0], team[1][0], team[1][1], team[1][2])
        #     file.write(str(team) + "\n")
            # print(team)

# Look up effectiveness from dict
def lookupEffects(pkmn, dict):
    if pkmn.type2 == "":
        pkmn.effects = dict[pkmn.type1]
    else:
        if pkmn.types in dict:
            pkmn.effects = dict[pkmn.types]
        else:
            pkmn.effects = dict[pkmn.typesR]

# Kivy GUI -------------------------------------------------------------------------------------------------------------
class MyLayout(BoxLayout):
    teams_data = ListProperty([])
    type1_input = ObjectProperty(None)
    type2_input = ObjectProperty(None)
    old_filter_input = ObjectProperty(None)
    new_filter_input = ObjectProperty(None)
    color = ColorProperty(typecolors["none"])
    submit = ObjectProperty(None)
    #status = ObjectProperty(None)
    rsort = ObjectProperty(None)
    #psort = ObjectProperty(None)
    wsort = ObjectProperty(None)
    usort = ObjectProperty(None)
    #tdatatext = ObjectProperty(None)
    #spinopts = ObjectProperty(size_hint_y=None, height=25)

    calculated = False

    def spinner1_clicked(self, type):
        self.ids.type1_input.background_color = kivy.utils.get_color_from_hex(typecolors[type])
        #self.ids.option_cls = spinopts

    def spinner2_clicked(self, type):
        self.ids.type2_input.background_color = kivy.utils.get_color_from_hex(typecolors[type])

    def press(self):
        # Update status text before any calc
        type1_input = self.type1_input.text
        type2_input = self.type2_input.text

        if type1_input == 'none' and type2_input == 'none':
            self.ids.status.text = '< No types! Select and submit types! >'
            print('No types! Select and submit types! ')
            return
        else:
            #self.submit.disabled = True
            self.ids.status.text = '< Calculating... >'

    def release(self):
        # Check types input before calc
        type1_input = self.type1_input.text
        type2_input = self.type2_input.text
        self.calculated = False

        print(f'Pokemon type 1 is {type1_input}, type 2 is {type2_input}!')
        if type1_input == 'none' and type2_input == 'none':
            #no types (already updated status on press)
            return
        #ins.status = self.ids.status.text
        elif type1_input == 'none' and type2_input != 'none':
            # swap types and use ''
            calculate(type2_input,'')
        elif (type1_input != 'none' and type2_input == 'none') or type1_input == type2_input:
            # make type2 ''
            calculate(type1_input, '')
        else: #type1_input != 'none' and type2_input == 'none' or type1_input == type2_input:
            # calc as normal
            calculate(type1_input, type2_input)

        self.calculatedText = '< Calculated! Top 10% rated teams including ' + str(noWeakTeamsNum) + ' with no weaks, ' + str(oneWeakTeamsNum) + ' with one.' + ' >'
        self.get_dataframe(rsort1, self.calculatedText)

    # Update status text before any sort
    def sort_press(self):
        # Don't sort if no data
        if len(self.teams_data) == 0:
            self.ids.status.text = '< No data to sort! Select and submit types! >'
            return
        else:
            self.ids.status.text = '< Sorting... >'

    # Function to sort on sort button presses
    def sort_release(self, field, arrow):
        #print(field, arrow)
        # Don't sort if no data
        if len(self.teams_data) == 0:
            #no types (already updated status on press)
            return
        else:
            # Sort based on field and arrow position (could make this into loop with format/dict)
            if field == 'r':
                if arrow == '^':
                    self.rsort.text = 'v'
                    self.new_filter_input.text = 'any'
                    self.wsort.text = '-'
                    self.usort.text = '-'
                    self.get_dataframe(rsort2, '< Sorted by worst to best rating! >')
                else:
                    self.rsort.text = '^'
                    self.new_filter_input.text = 'any'
                    self.wsort.text = '-'
                    self.usort.text = '-'
                    self.get_dataframe(rsort1, '< Sorted by best to worst rating! >')
            # elif field == 'p':
            #     if arrow == '^':
            #         self.rsort.text = '-'
            #         self.psort.text = 'v'
            #         self.wsort.text = '-'
            #         self.usort.text = '-'
            #         self.get_dataframe(psort2, '< Sorted by ally pokemon types descending! >')
            #     else:
            #         self.rsort.text = '-'
            #         self.psort.text = '^'
            #         self.wsort.text = '-'
            #         self.usort.text = '-'
            #         self.get_dataframe(psort1, '< Sorted by ally pokemon types ascending! >')
            elif field == 'w':
                if arrow == '^':
                    self.rsort.text = '-'
                    self.new_filter_input.text = 'any'
                    self.wsort.text = 'v'
                    self.usort.text = '-'
                    self.get_dataframe(wsort2, '< Sorted by most to least weaknesses! >')
                else:
                    self.rsort.text = '-'
                    self.new_filter_input.text = 'any'
                    self.wsort.text = '^'
                    self.usort.text = '-'
                    self.get_dataframe(wsort1, '< Sorted by least to most weaknesses! >')
            else:
                if arrow == '^':
                    self.rsort.text = '-'
                    self.new_filter_input.text = 'any'
                    self.wsort.text = '-'
                    self.usort.text = 'v'
                    self.get_dataframe(usort2, '< Sorted by most to least unresists! >')
                else:
                    self.rsort.text = '-'
                    self.new_filter_input.text = 'any'
                    self.wsort.text = '-'
                    self.usort.text = '^'
                    self.get_dataframe(usort1, '< Sorted by least to most unresists! >')

    def filter_clicked(self):
        # Don't filter if no data
        new_filter_input = self.new_filter_input.text

        if len(self.teams_data) == 0:
            self.ids.status.text = '< No data to filter! Select and submit types! >'
            return
        elif new_filter_input == self.old_filter_input:
            # no need to change or filter anything
            return
        else:
            self.old_filter_input = new_filter_input
            self.ids.status.text = '< Filtering... >'
            self.rsort.text = '-'
            self.wsort.text = '-'
            self.usort.text = '-'
            if new_filter_input == 'any':
                self.get_dataframe(rsort1, '< Sorted by best to worst rating! >')
            else:
                pfilter = list(filter(lambda x: new_filter_input in x[0], teamsDict2.items()))
                if len(pfilter) == 0:
                    self.ids.status.text = '< No filterable ' + new_filter_input + ' type allies in top 10%! >'
                    return
                else:
                    self.get_dataframe(pfilter, '< Filtered by allies with ' + new_filter_input + ' type! >')

    # def filter_press(self):
    #     # Don't filter if no data
    #     filter_input = self.filter_input.text
    #
    #     if len(self.teams_data) == 0:
    #         self.ids.status.text = '< No data to filter! Select and submit types! >'
    #         return
    #     else:
    #         self.ids.status.text = '< Filtering... >'

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        #self.ids.status.text = 'Initialized. Select and submit types!'

    # Function to update sorted data
    def get_dataframe(self, currentsort, message):
        # Clear previous data
        self.teams_data = []
        #self.tdatatext.font_size = sp(10)

        # Output sorted data, with type color markups
        #[\['\]]|ing|tric|on|chic|al|nd
        i = 0
        while i < len(currentsort):
            rating = str(currentsort[i][1]['rating'])
            self.teams_data.append({'text': rating, 'index': rating, 'size_hint_x': None, 'width': kivy.metrics.dp(35), 'font_size': kivy.metrics.sp(10)})
            team = currentsort[i][0]
            for key, value in typecolors.items():
                team = re.sub(str(key), str("[color="+str(value)+"]"+str(key)+"[/color]"), str(team))
            self.teams_data.append({'markup': True, 'text': team, 'index': team, 'font_size': kivy.metrics.sp(10)})
            tweaks = re.sub("[\['\]]", "", str(currentsort[i][1]['tweaks']))
            for key, value in typecolors.items():
                tweaks = re.sub(str(key), str("[color=" + str(value) + "]" + str(key) + "[/color]"), str(tweaks))
            self.teams_data.append({'markup': True, 'text': tweaks, 'index': tweaks, 'font_size': kivy.metrics.sp(8)})
            tURs = re.sub("[\['\]]", "", str(currentsort[i][1]['tURs']))
            for key, value in typecolors.items():
                tURs = re.sub(str(key), str("[color=" + str(value) + "]" + str(key) + "[/color]"), str(tURs))
            self.teams_data.append({'markup': True, 'text': tURs, 'index': tURs, 'font_size': kivy.metrics.sp(6)})
            i+=1
        self.teams_data.append({'text': '', 'index': '', 'size_hint_x': None, 'width': kivy.metrics.dp(35)})
        #print(self.teams_data)
        self.ids.status.text = message
        if not self.calculated:
            self.rsort.text = '^'
            self.new_filter_input.text = 'any'
            self.wsort.text = '-'
            self.usort.text = '-'
        #self.submit.disabled = False
        self.calculated = True


# class MyClass(EventDispatcher):
#     status = ObjectProperty(None)
#
#     def on_a(self, instance, value):
#         app = App.get_running_app()
#         app.status.text = str(value)
#
# def callback(instance, value):
#     print('My callback is call from', instance)
#     print('and the a value changed to', value)
#
# ins = MyClass()
# ins.bind(status=callback)

class main(App):
    def build(self):
        intitialize()
        return MyLayout()


if __name__ == "__main__":
    main().run()