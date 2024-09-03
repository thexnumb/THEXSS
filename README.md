# THEXSS python script
Simple parameter reflection detection for finding XSS.
This python script help you to test for low-hanging fruits of XSS on a given URL.

## Installing requirements
```bash
    python3 -m pip install -r requirements.txt
```
- Note that the best way for installing packages is to set environment for those packages as below.
    ```bash
        python3 -m venv name # you can put any name you want instead of this
        venv\Scripts\activate # if you are on Windows machine use this for activate
        source venv/bin/activate # if you are on Linux (macOS) machine use this for activate
        deactivate # when you want to deactivate the virtual environment
    ```

## Usage
- you can use `thexss.py -u GIVEN_URL` to get all reflection parameters.
- you also can the full usage with the `-h` switch

## Checklist for Feature
- [ ] Improve finding paramter method
- [ ] Adding the test engine for XSS

## Contact
- You can connect with me for any suggestion via my [Twitter](https://x.com/thexsecurity) or [Telegram](https://t.me/thexnumb) accounts.
