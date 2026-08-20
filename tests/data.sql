INSERT INTO users (username, hash)
 VALUES ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
        ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO tournaments (name, season)
 VALUES ('Tournament 1', '2022/23'),
        ('Tournament 1', '2023/24');

INSERT INTO teams (name)
 VALUES ('Team 1'),
        ('Team 2'),
        ('Team 3'),
        ('Team 4');

INSERT INTO matches (tournament_id, home_team_id, away_team_id, match_date)
 VALUES ('1', '1', '2', '2018-01-01 00:00:00'),
        ('1', '2', '3', '2018-01-01 00:00:00');

INSERT INTO predictions (user_id, match_id, home_score, away_score)
 VALUES ('1', '1', '1', '0'),
        ('2', '2', '2', '1');
