import os
import subprocess
import ffmpeg

print("Путь: ")
directory = input()
files = os.listdir(directory)

videos = list(filter(lambda file: file.endswith(".mkv"), files))
fonts = os.listdir(directory + "\\fonts")
print("Найдены файлы с названиями {}".format(videos[0]))
print("Укажите маску для новых названий: ")
mask = input()
ep_no = 1
for vid in videos:
    base_name = vid[:-4]
    sub = base_name + ".ass"
    probe = ffmpeg.probe(os.path.join(directory, vid))
    nb_streams = probe["format"]["nb_streams"]
    # В контейнере содержится nb_streams потоков. Каждый новый аттач = +1 поток
    cmd = "ffmpeg "
    # Добавляем контейнер видео/аудио, субтитры
    cmd += '-i "{}" '.format(os.path.join(directory, vid))
    cmd += '-i "{}" '.format(os.path.join(directory, sub))
    nb_streams += 1
    # Устанавливаем метку по умолчанию для сабов
    cmd += "-disposition:s:{} default ".format(nb_streams - 1)
    # Устанавливаем язык субтитров русский
    cmd += "-metadata:s:{} language=ru ".format(nb_streams - 1)
    # Аттачим все шрифты, помечая metadata для соответствующих потоков. Каждый аттач = поток
    for font in fonts:
        cmd += '-attach "{}" -metadata:s:{} mimetype=application/x-truetype-font '.format(
            os.path.join(directory, "fonts", font), nb_streams
        )
        nb_streams += 1
    # Не перекодировать видео, аудио
    cmd += "-c:v copy -c:a copy "
    cmd += ('"' + mask + '.mkv"').format(ep_no)
    ep_no += 1
    print(cmd)
    exit_code = subprocess.call(cmd)
    if exit_code != 0:
        print("Что-то не так! Код {}".format(exit_code))
