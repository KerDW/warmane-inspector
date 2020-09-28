import PySimpleGUI as sg
import asyncio
from pyppeteer import launch
import os
import requests
from bs4 import BeautifulSoup
import re

async def screenshotSpecs(name, realm):
    browser = await launch(headless=True)
    page = await browser.newPage()

    # talent screenshots
    base_url = 'https://armory.warmane.com/character/'+name+'/'+realm+'/'

    await page.goto(base_url+'talents')
    # focus page to avoid tooltips
    await page.bringToFront()

    talent_selector = await page.querySelector('#character-sheet > table > tbody > tr > td:nth-child(1) > a')

    if talent_selector is not None:
        # change spec through js click (if currently in OS it'll error)
        await page.click('#character-sheet > table > tbody > tr > td:nth-child(1) > a')
        await page.mouse.move(0, 0)

        # get mainspec and save screenshot
        await page.waitForSelector('#spec-0')
        element = await page.querySelector('#spec-0')  
        await element.screenshot({'path': 'talents0.png'})

        # change spec through js click
        await page.click('#character-sheet > table > tbody > tr > td:nth-child(3) > a')
        await page.mouse.move(0, 0)

        # screenshot offspec
        await page.waitForSelector('#spec-1')
        element = await page.querySelector('#spec-1')
        await element.screenshot({'path': 'talents1.png'})
    else:
        # get mainspec and save screenshot
        main_spec_selector = await page.querySelector('#spec-0')
        if main_spec_selector is not None:
            element = await page.querySelector('#spec-0')  
            await element.screenshot({'path': 'talents0.png'})
        else:
            # no mainspec talents means character not found, close
            await browser.close()
            return 0
    await browser.close()
    return 1

base_layout = [  
    [sg.Combo(['Lordaeron', 'Frostmourne', 'Icecrown', "Blackrock"], default_value="Lordaeron", enable_events=True, key='combo'), sg.Text('Character:'), sg.InputText(), sg.Checkbox('Talents img', enable_events=True, key='talents'), sg.Button('Inspect', bind_return_key=True)]
]

window = sg.Window('Warmane inspector', base_layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "Inspect":

        character_name = values[0].capitalize()
        realm = values['combo']
        talents_cb = values['talents']
        base_url = 'https://armory.warmane.com/character/'+character_name+'/'+realm+'/'

        html_page = requests.get(base_url+"profile")
        soup = BeautifulSoup(html_page.content, 'html.parser')

        # check if name is there and therefore we got a profile
        name = soup.find('span', {'class': 'name'})

        if name is not None:

            if talents_cb is True:
                asyncio.get_event_loop().run_until_complete(screenshotSpecs(character_name, realm))

            guild_name = soup.find('span', {'class': 'guild-name'}).text

            level_race_class = soup.find('div', {'class': 'level-race-class'}).text

            spec = soup.find_all('div', {'class': 'specialization'})
            spec_text = ""

            for tag in spec:
                tags = tag.find_all("div", {"class": "text"})
                for tag in tags:
                    spec_text = spec_text + tag.text

            prof = soup.find_all('div', {'class': 'profskills'})
            prof_text = ""

            for tag in prof:
                tags = tag.find_all("div", {"class": "text"})
                for tag in tags:
                    prof_text = prof_text + tag.text

            stats = soup.find_all('div', {'class': 'character-stats'})
            core_stats_text = ""
            stats_text_first_part = ""
            stats_text_second_part = ""
            stats_text_third_part = ""
            i = 0

            for tag in stats:
                tags = tag.find_all("div", {"class": "text"})
                for tag in tags:
                    if i == 0:
                        stats_text_first_part = stats_text_first_part + tag.text
                    elif i == 1:
                        stats_text_second_part = stats_text_second_part + tag.text
                    elif i == 2:
                        stats_text_third_part = stats_text_third_part + tag.text
                    i += 1

            first_stats_array = stats_text_first_part.split()
            second_stats_array = stats_text_second_part.split()
            third_stats_array = stats_text_third_part.split()
            core_stats_text = "Melee/Ranged Hit Rating: "+first_stats_array[11]+"\nExpertise: "+first_stats_array[26]
            core_stats_text = core_stats_text + "\nSpell Hit Rating: "+third_stats_array[9]+"\nSpell Haste: "+third_stats_array[6]
            core_stats_text = core_stats_text + "\nArmor: "+second_stats_array[16]

            toc_category = {'category': '15021'}
            toc_data = requests.post(base_url+"statistics", toc_category)
            toc_data_text = toc_data.text

            icc_category = {'category': '15062'}
            icc_data = requests.post(base_url+"statistics", icc_category)
            icc_data_text = icc_data.text

            # togc info wrong on the database apparently, killing on any difficulty counts for all of them
            toc_bosses = ['Victories over the Beasts of Northrend (Trial of the Crusader 25 player)', 'Lord Jaraxxus kills (Trial of the Crusader 25 player)', 
            'Victories over the Faction Champions (Trial of the Crusader 25 player)', "Val'kyr Twins kills (Trial of the Crusader 25 player)", 
            'Times completed the Trial of the Crusader (25 player)', "Victories over the Beasts of Northrend (Trial of the Grand Crusader 10 player)", 
            "Lord Jaraxxus kills (Trial of the Grand Crusader 10 player)", "Victories over the Faction Champions (Trial of the Grand Crusader 10 player)", 
            "Val'kyr Twins kills (Trial of the Grand Crusader 10 player)", "Times completed the Trial of the Grand Crusader (10 player)", 
            "Victories over the Beasts of Northrend (Trial of the Grand Crusader 25 player)", 
            "Lord Jaraxxus kills (Trial of the Grand Crusader 25 player)", "Victories over the Faction Champions (Trial of the Grand Crusader 25 player)", 
            "Val'kyr Twins kills (Trial of the Grand Crusader 25 player)", "Times completed the Trial of the Grand Crusader (25 player)",
            ]
            toc_bosses_kills = []

            # loop over bosses and find the nearest number after it, which will always be the kill count
            for boss in toc_bosses:
                boss_pos = toc_data_text.find(boss)
                boss_kills_pos = toc_data_text.find('">', boss_pos)
                try:
                    toc_bosses_kills.append(re.search('\d+', toc_data_text[boss_kills_pos:boss_kills_pos+7]).group(0))
                except:
                    toc_bosses_kills.append(0)

            toc_25_bosses_completion = 5 - toc_bosses_kills[0:5].count(0)
            # togc_10_bosses_completion = 5 - toc_bosses_kills[5:10].count(0)
            # togc_25_bosses_completion = 5 - toc_bosses_kills[10:15].count(0)

            icc_bosses = [
                "Lord Marrowgar kills (Icecrown 10 player)", "Lady Deathwhisper kills (Icecrown 10 player)", "Gunship Battle victories (Icecrown 10 player)",
                "Deathbringer kills (Icecrown 10 player)", "Rotface kills (Icecrown 10 player)", "Festergut kills (Icecrown 10 player)", "Professor Putricide kills (Icecrown 10 player)",
                "Blood Prince Council kills (Icecrown 10 player)", "Blood Queen Lana'thel kills (Icecrown 10 player)", "Valithria Dreamwalker rescues (Icecrown 10 player)",
                "Sindragosa kills (Icecrown 10 player)", "Victories over the Lich King (Icecrown 10 player)",
                "Lord Marrowgar kills (Icecrown 25 player)", "Lady Deathwhisper kills (Icecrown 25 player)", "Gunship Battle victories (Icecrown 25 player)",
                "Deathbringer kills (Icecrown 25 player)", "Rotface kills (Icecrown 25 player)", "Festergut kills (Icecrown 25 player)", "Professor Putricide kills (Icecrown 25 player)",
                "Blood Prince Council kills (Icecrown 25 player)", "Blood Queen Lana'thel kills (Icecrown 25 player)", "Valithria Dreamwalker rescues (Icecrown 25 player)",
                "Sindragosa kills (Icecrown 25 player)", "Victories over the Lich King (Icecrown 25 player)",
                "Lord Marrowgar kills (Heroic Icecrown 10 player)", "Lady Deathwhisper kills (Heroic Icecrown 10 player)", "Gunship Battle victories (Heroic Icecrown 10 player)",
                "Deathbringer kills (Heroic Icecrown 10 player)", "Rotface kills (Heroic Icecrown 10 player)", "Festergut kills (Heroic Icecrown 10 player)", "Professor Putricide kills (Heroic Icecrown 10 player)",
                "Blood Prince Council kills (Heroic Icecrown 10 player)", "Blood Queen Lana'thel kills (Heroic Icecrown 10 player)", "Valithria Dreamwalker rescues (Heroic Icecrown 10 player)",
                "Sindragosa kills (Heroic Icecrown 10 player)", "Victories over the Lich King (Heroic Icecrown 10 player)",
                "Lord Marrowgar kills (Heroic Icecrown 25 player)", "Lady Deathwhisper kills (Heroic Icecrown 25 player)", "Gunship Battle victories (Heroic Icecrown 25 player)",
                "Deathbringer kills (Heroic Icecrown 25 player)", "Rotface kills (Heroic Icecrown 25 player)", "Festergut kills (Heroic Icecrown 25 player)", "Professor Putricide kills (Heroic Icecrown 25 player)",
                "Blood Prince Council kills (Heroic Icecrown 25 player)", "Blood Queen Lana'thel kills (Heroic Icecrown 25 player)", "Valithria Dreamwalker rescues (Heroic Icecrown 25 player)",
                "Sindragosa kills (Heroic Icecrown 25 player)", "Victories over the Lich King (Heroic Icecrown 25 player)"
            ]
            icc_bosses_kills = []

            # loop over bosses and find the nearest number after it, which will always be the kill count
            for boss in icc_bosses:
                boss_pos = icc_data_text.find(boss)
                boss_kills_pos = icc_data_text.find('">', boss_pos)
                # data has - - to represent 0 so if no number found it's 0
                try:
                    icc_bosses_kills.append(re.search('\d+', icc_data_text[boss_kills_pos:boss_kills_pos+7]).group(0))
                except:
                    icc_bosses_kills.append(0)

            icc_10_bosses_completion = 12 - icc_bosses_kills[0:12].count(0)
            icc_25_bosses_completion = 12 - icc_bosses_kills[12:24].count(0)
            icc_10_hc_bosses_completion = 12 - icc_bosses_kills[24:36].count(0)
            icc_25_hc_bosses_completion = 12 - icc_bosses_kills[36:48].count(0)

            main_tab_layout = [[sg.Text("Character: "+character_name), sg.Text("\t\t\t\t\t"), sg.Text(spec_text)],
                                [sg.Text(level_race_class)],
                                [sg.Text("Guild: "+guild_name)],
                                [sg.Text(core_stats_text), sg.Text("\t\t\t\t"), sg.Text(prof_text)],
                                [sg.Text("\nToC 25: " + str(toc_25_bosses_completion) + "/5")],
                                # [sg.Text("ToGC 10: " + str(togc_10_bosses_completion) + "/5")],
                                # [sg.Text("ToGC 25: " + str(togc_25_bosses_completion) + "/5")],
                                [sg.Text("ICC 10: " + str(icc_10_bosses_completion) + "/12")],
                                [sg.Text("ICC 25: " + str(icc_25_bosses_completion) + "/12")],
                                [sg.Text("ICC 10 HC: " + str(icc_10_hc_bosses_completion) + "/12")],
                                [sg.Text("ICC 25 HC: " + str(icc_25_hc_bosses_completion) + "/12")]
                                ]

            stats_tab_layout = [[sg.Text("Stats:")],
                [sg.Text(stats_text_first_part), sg.Text(stats_text_second_part), sg.Text(stats_text_third_part)]
            ]

            if talents_cb:
                talents = []

                if os.path.exists(os.getcwd()+'\\'+'talents1.png'):
                    talents = [sg.Image(os.getcwd()+'\\'+'talents0.png'), sg.Image(os.getcwd()+'\\'+'talents1.png')]
                else:
                    talents = [sg.Image(os.getcwd()+'\\'+'talents0.png')]

                talents_tab_layout = [[sg.Text("Talents:")],
                                        talents
                                    ]

            # raids_tab_layout = [
                
            # ]
 
            if talents_cb:
                layout_success = [
                    [sg.TabGroup([[sg.Tab('Main', main_tab_layout), sg.Tab('Stats', stats_tab_layout), sg.Tab('Talents', talents_tab_layout)]])]
                ]
            else:
                layout_success = [
                    [sg.TabGroup([[sg.Tab('Main', main_tab_layout), sg.Tab('Stats', stats_tab_layout)]])]
                ]

            window2 = sg.Window('Character info - '+character_name, layout_success)

            while True:
                event2, values2 = window2.read()
                if event2 == sg.WIN_CLOSED:
                    break

            window2.close()

            if talents_cb:
                os.remove('talents0.png')
                if os.path.exists(os.getcwd()+'\\'+'talents1.png'):
                    os.remove('talents1.png')

        else:

            layout_fail = [
                [sg.Text("Couldn't find the character")],
                [sg.Button('OK', bind_return_key=True)]
            ] 

            window3 = sg.Window('Character info', layout_fail)
            while True:
                event3, values3 = window3.read()
                if event3 == "OK" or event == sg.WIN_CLOSED:
                    break

            window3.close()
        
window.close()