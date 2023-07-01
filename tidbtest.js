var mysql = require('mysql2');

var connection = mysql.createConnection({
  host: 'gateway01.eu-central-1.prod.aws.tidbcloud.com',
  port: 4000,
  user: '4P4Mongv3vUVSHz.root',
  password: 'tRc1r5kwywCUMk2c',
  database: 'test',
  ssl: {
    minVersion: 'TLSv1.2',
    rejectUnauthorized: true
  }
});
connection.connect(function(err) {
  if (err) {
    throw err
  }
  connection.query('SELECT DATABASE();', function(err, rows) {
    if (err) {
      throw err
    }
    console.log(rows[0]['DATABASE()']);
    connection.end()
  });
});