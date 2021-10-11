# biblio

## Data
- Книги (смёрженные, почищененные и обогащённые uniq_id): https://www.dropbox.com/s/tswgy8ppf6bbpn6/refined_books.jsonl.tar.gz
- Большая библиотечная база (книги и экшены): https://www.dropbox.com/s/se6zn98ulv3ga0w/other_actions.tar.gz
- Книги с mos.ru: https://www.dropbox.com/s/bm87xst2bn084t8/items.json
- Экшены с mos.ru: https://www.dropbox.com/s/gl5z0s4q7h9kyll/actions.csv

## Backend
### Docker Compose install
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Launch
```
mkdir data
sudo docker-compose up
```

### Manually examining containers
`sudo docker exec -it <containername> bash`
