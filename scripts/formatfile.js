const fs = require('fs');
const os = require('os');

fs.readFile('./image_list.yml', 'utf-8', (err, data) => {
  if(err) {
    console.log('read fail');
    return;
  }
  fs.unlinkSync('../examples/image_list_temp.yml', (err) => {
    if(err) {
      console.log('clear fail');
      return;
    }
  });
  let dataSource = data.split(os.EOL).filter(item => item);
  dataSource.map(row => {
    const rowContent = row.split('/');
    fs.appendFile('../examples/image_list_temp.yml', `- {url: 'http://192.168.2.2:8024/static/data/temp_pic/${rowContent[rowContent.length - 1]}'}\n`, (err) => {
      if(err) {
        console.log('append fail');
      }
    });
  });
  console.log('append success');
});
