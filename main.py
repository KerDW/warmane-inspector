import PySimpleGUI as sg
import asyncio
from pyppeteer import launch
import os

async def screenshotSpecs(name):
    browser = await launch()
    page = await browser.newPage()

    try:
        await page.goto('https://armory.warmane.com/character/'+name+'/Lordaeron/talents')
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
    if asyncio.get_event_loop().run_until_complete(screenshotSpecs(values[0])) == True:

        popup_success = [
            [sg.Text("Character Name: "+values[0])],
            [sg.Text("Talents:")],
            [sg.Image(os.getcwd()+'\\'+'talents0.png'), sg.Image(os.getcwd()+'\\'+'talents1.png')]
        ]

        window2 = sg.Window('Character info', popup_success)
        while True:
            event2, values2 = window2.read()
            if event2 == sg.WIN_CLOSED:
                break

        window2.close()

    else:

        popup_fail = [
            [sg.Text("Couldn't find the character")],
            [sg.Button('OK', bind_return_key=True)]
        ] 

        window3 = sg.Window('Character info', popup_fail)
        while True:
            event3, values3 = window3.read()
            if event3 == "OK" or event == sg.WIN_CLOSED:
                break

        window3.close()
        
window.close()