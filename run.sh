source .env
uvicorn src.main:app --reload
# docker run  -e DD_SITE -e DD_API_KEY -e SLACK_TOKEN -it -p 80:80 slack-emoji-stats --name  emoji-stats