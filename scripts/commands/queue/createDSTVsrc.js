const axios = require('axios')
var builder = require('xmlbuilder');

const {file, parser} = require('../../core')

const CHANNELS_PATH = "sites/dstv.com/*.channels.xml"

async function channels() {
  const data = await axios
    .get(
      `https://www.dstv.com/umbraco/api/TvGuide/GetChannels?country=zaf&unit=dstv`
    )
    .then(r => r.data)
    .catch(console.log)
  console.log(data);
  return data.Channels.map(item => {
    return {
      site_id: `zaf#${item.Number}`,
      name: item.Name,
      tag: item.Tag,
      icon: item.Logo
    }
  })
}

async function main() {
  const files = await file.list(CHANNELS_PATH)

  for (const filepath of files) {
    try {
      console.log(filepath)
      const dir = file.dirname(filepath)
      const {
        site,
        channels: items
      } = await parser.parseChannels(filepath)
      if (!site) continue
      const configPath = `${dir}/${site}.config.js`
      const config = require(file.resolve(configPath))
      var data = await config.rawChannels("zaf")
      const xmlobj = {
        ...data.map((item) => {
          return {
            '@lang': 'en',
            '@xmltv_id': item.tag,
            '@site_id': item.site_id,
            '#text': item.name
          }
        })
      }

      var obj = {
        site: {
          channels: [
            Object.values(xmlobj)
          ]
        }
      };

      const xml = builder.create(obj).end({
        pretty: true
      });

      await file.create(filepath, xml)

      //console.log(xml)


    } catch (err) {
      console.error(err)
    }
  }
}

main()