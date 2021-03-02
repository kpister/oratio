## DeepL Translator

- Create an account in [(DeepL Pro)](https://www.deepl.com/pro?cta=menu-login-signup).
- For Free Trial (Click `Start Free Trial` and Select an Plan), follow the steps andelect the plan for one month.
- Once you verify your address and other details, Navigate to dashboard for DeepL API Key.
- Remember your DeepL API key (keep it safe!) and use URL [(https://api.deepl.com/v2/translate)](https://api.deepl.com/v2/translate). 
- With this API key you can create a wrapper fucntion.
- API call will be through ```curl/network requests```.

EXAMPLE REQUEST
```
curl https://api.deepl.com/v2/translate \ 
	-d auth_key=[yourAuthKey] \ 
	-d "text=Hello, world"  \ 
	-d "target_lang=DE"
```
EXAMPLE RESPONSE
JSON Representation
```
{
	"translations": [{
		"detected_source_language":"EN",
		"text":"Hallo, Welt!"
	}]
}
```
For more details about DeepL translator request, response, authentication, etc. Refer to [(https://www.deepl.com/docs-api/)](https://www.deepl.com/docs-api/accessing-the-api/authentication/)