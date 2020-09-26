import PySimpleGUI as sg
import asyncio
from pyppeteer import launch
import os
import requests
from bs4 import BeautifulSoup

async def screenshotSpecs(name):
    browser = await launch(headless=True)
    page = await browser.newPage()

    # talent screenshots
    try:
        base_url = 'https://armory.warmane.com/character/'+name+'/Lordaeron/'

        await page.goto(base_url+'talents')
        # focus page to avoid tooltips
        await page.bringToFront()

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

        return 1
    except:
        await browser.close()
        return 0

base_layout = [  
    [sg.Text('Character:'), sg.InputText(), sg.Button('Inspect', bind_return_key=True)]
]

window = sg.Window('Warmane inspector', base_layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "Inspect":

        character_name = values[0].capitalize()

        if asyncio.get_event_loop().run_until_complete(screenshotSpecs(character_name)) == True:

            base_url = 'https://armory.warmane.com/character/'+character_name+'/Lordaeron/'

            html_page = requests.get(base_url+"profile")
            soup = BeautifulSoup(html_page.content, 'html.parser')

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
            core_stats_text = core_stats_text + "\nSpell Hit Rating: "+third_stats_array[9]
            core_stats_text = core_stats_text + "\nArmor: "+second_stats_array[16]

            main_tab_layout = [[sg.Text("Character: "+character_name)],
                                [sg.Text(level_race_class)],
                                [sg.Text("Guild: "+guild_name)],
                                [sg.Text("Specs: "+spec_text)],
                                [sg.Text("Profs: "+prof_text)],
                                [sg.Text("Core stats: ")],
                                [sg.Text(core_stats_text)]
                                ]

            stats_tab_layout = [[sg.Text("Stats:")],
                [sg.Text(stats_text_first_part), sg.Text(stats_text_second_part), sg.Text(stats_text_third_part)]
                ]

            talents_tab_layout = [[sg.Text("Talents:")],
                [sg.Image(os.getcwd()+'\\'+'talents0.png'), sg.Image(os.getcwd()+'\\'+'talents1.png')]]

 
            layout_success = [
                [sg.TabGroup([[sg.Tab('Main', main_tab_layout), sg.Tab('Stats', stats_tab_layout), sg.Tab('Talents', talents_tab_layout)]])]
            ]

            window2 = sg.Window('Character info - '+character_name, layout_success)
            while True:
                event2, values2 = window2.read()
                if event2 == sg.WIN_CLOSED:
                    break

            window2.close()

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