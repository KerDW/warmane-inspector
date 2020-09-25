import PySimpleGUI as sg
import asyncio
from pyppeteer import launch
import os

async def screenshotSpecs(name):
    browser = await launch(headless=True)
    page = await browser.newPage()

    try:
        await page.goto('https://armory.warmane.com/character/'+name+'/Lordaeron/talents')

        # change spec through js click (if currently in OS it'll error)
        await page.click('#character-sheet > table > tbody > tr > td:nth-child(1) > a')

        # get mainspec and save screenshot
        await page.waitForSelector('#spec-0')
        element = await page.querySelector('#spec-0')
        await element.screenshot({'path': 'talents0.png'})

        # change spec through js click
        await page.click('#character-sheet > table > tbody > tr > td:nth-child(3) > a')

        # screenshot offspec
        await page.waitForSelector('#spec-1')
        element = await page.querySelector('#spec-1')
        await element.screenshot({'path': 'talents1.png'})

        return 1
    except:
        await browser.close()
        return 0

def base_window():
    base_layout = [  
        [sg.Text('Character:'), sg.InputText(), sg.Button('Inspect')],
        [sg.Button('Submit', visible=False, bind_return_key=True)]
    ]

    window = sg.Window('Warmane inspector', base_layout)

    return window

def window_success():
    layout_success = [
        [sg.Text("Character Name: "+values[0])],
        [sg.Text("Talents:")],
        [sg.Image(os.getcwd()+'\\'+'talents0.png'), sg.Image(os.getcwd()+'\\'+'talents1.png')]
    ]

    window = sg.Window('Character info', layout_success)

    return window

def window_fail():
    popup_fail = [
        [sg.Text("Couldn't find the character")],
        [sg.Button('OK')],
        [sg.Button('Submit', visible=False, bind_return_key=True)]
    ] 

    window = sg.Window('Character info', popup_fail)

    return window

window = base_window()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Inspect' or event == 'Submit':

        if asyncio.get_event_loop().run_until_complete(screenshotSpecs(values[0])) == True:

            window_success = window_success()

            while True:
                event2, values2 = window_success.read()
                if event2 == sg.WIN_CLOSED:
                    break

            window_success.close()

        else:

            window_fail = window_fail()

            while True:
                event3, values3 = window_fail.read()
                if event3 == "OK" or event3 == "Submit" or event == sg.WIN_CLOSED:
                    break

            window_fail.close()
        
window.close()