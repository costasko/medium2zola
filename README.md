# medium2zola
Convert a medium.com export to markdown - tested with https://www.getzola.org/  - Should work with Jekyll, Hugo, etc.

1. Export your account data https://help.medium.com/hc/en-us/articles/115004745787-Export-your-account-data
2. Unzip your content
3. Navigate inside the folder and copy `converter.py`. Your tree structure should look like this
```sh
posts/
├─ 2018-11-04_My_medium_post.html
├─ 2020-10-10_Other_post.html
converter.py
```
4. ```sh
   python3 -m venv env $$ source env/bin/activate && pip install 
   pip install pypandoc==1.11 requests==2.31.0
   python converter.py
   ```

The script will 
- [x] Create a folder for each post
- [x] Convert the HTML to markdown
- [x] Download the images and link them correctly
- [x] Cleanup the markdown
