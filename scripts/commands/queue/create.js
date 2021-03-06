const { db, file, parser, logger, date, api } = require('../../core')
const { program } = require('commander')
const _ = require('lodash')

const options = program
  .option(
    '--max-clusters <max-clusters>',
    'Set maximum number of clusters',
    parser.parseNumber,
    256
  )
  .option('--days <days>', 'Number of days for which to grab the program', parser.parseNumber, 1)
  .parse(process.argv)
  .opts()

const CHANNELS_PATH = process.env.CHANNELS_PATH || 'sites/**/*.channels.xml'
const LOGS_DIR = process.env.LOGS_DIR || 'scripts/logs'

async function main() {
  logger.info('Starting...')
  logger.info(`Number of clusters: ${options.maxClusters}`)

  await saveToDatabase(await createQueue())

  logger.info('Done')
}

main()

async function createQueue() {
  logger.info(`Create queue...`)

  let queue = {}

  await api.channels.load()
  const files = await file.list(CHANNELS_PATH)
  const utcDate = date.getUTC()
  const dates = Array.from({ length: options.days }, (_, i) => utcDate.add(i, 'd'))
  for (const filepath of files) {
    try {
      const dir = file.dirname(filepath)
      const { site, channels: items } = await parser.parseChannels(filepath)
      if (!site) continue
      const configPath = `${dir}/${site}.config.js`
      const config = require(file.resolve(configPath))
      if (config.ignore) continue
      const filename = file.basename(filepath)
      const [__, region] = filename.match(/_([a-z-]+)\.channels\.xml/i) || [null, null]
      const groupId = `${region}/${site}`
      for (const item of items) {
        //logger.info(`Item ${item.xmltv_id}`)
        if (!item.site || !item.xmltv_id) continue
        var channel = api.channels.find({ id: item.xmltv_id })
        logger.info(`Channel ${channel}`)
        if (!channel) channel = true 
        if (!channel) continue
        for (const d of dates) {
          const dString = d.toJSON()
          const key = `${item.site}:${item.lang}:${item.xmltv_id}:${dString}`
          logger.info(`Key ${key}`)
          if (!queue[key]) {
            queue[key] = {
              channel: {
                lang: item.lang,
                xmltv_id: item.xmltv_id,
                display_name: item.name,
                site_id: item.site_id,
                site: item.site
              },
              date: dString,
              configPath,
              groups: [],
              error: null
            }
          }

          if (!queue[key].groups.includes(groupId)) {
            queue[key].groups.push(groupId)
          }
        }
      }
    } catch (err) {
      console.error(err)
    }
  }

  queue = Object.values(queue)

  logger.info(`Added ${queue.length} items`)

  return queue
}

async function saveToDatabase(items = []) {
  logger.info('Saving to the database...')
  await db.queue.load()
  await db.queue.reset()
  let queue = []
  const chunks = split(_.shuffle(items), options.maxClusters)
  for (const [i, chunk] of chunks.entries()) {
    for (const item of chunk) {
      item.cluster_id = i + 1
      queue.push(item)
    }
  }

  queue = _.sortBy(queue, ['channel.lang', 'channel.site_id', 'date'])
  await db.queue.insert(queue)
}

function split(arr, n) {
  let result = []
  for (let i = n; i > 0; i--) {
    result.push(arr.splice(0, Math.ceil(arr.length / i)))
  }
  return result
}
