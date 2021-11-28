# ЛИДЕРЫ ЦИФРОВОЙ ТРАНСФОРМАЦИИ
[Задача 03](https://leaders2021.innoagency.ru/03/). Рекомендательная система для пользователей московскиих библиотек

## Data
- **Основной предобработанный набор**: https://www.dropbox.com/s/ijaqsf72ez2kpmn/refined_data_v5.tar.gz
- Большая библиотечная база (книги и экшены): https://www.dropbox.com/s/se6zn98ulv3ga0w/other_actions.tar.gz
- Книги с mos.ru: https://www.dropbox.com/s/bm87xst2bn084t8/items.json
- Экшены с mos.ru: https://www.dropbox.com/s/gl5z0s4q7h9kyll/actions.csv
- Дополнение к библиотечной базе (книги): https://www.dropbox.com/s/b2adss0k8n65stx/cat_3.csv
- Дополнение к библиотечной базе (экшены): https://www.dropbox.com/s/nrositd7ceqid7p/circulaton_3.csv

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
