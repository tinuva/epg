const { db, logger, file, api, zip } = require('../../core')
const grabber = require('epg-grabber')
const _ = require('lodash')

const PUBLIC_DIR = process.env.PUBLIC_DIR || '.gh-pages'

async function main() {
  logger.info(`Generating guides/...`)

  logger.info('Loading "database/programs.db"...')
  await db.programs.load()
  await api.channels.load()

  let total = 0
  const grouped = groupByGroup(await loadQueue())
  for (const key in grouped) {
    let channels = {}
    let programs = []
    for (const item of grouped[key]) {
      if (item.error) continue

      const itemPrograms = await loadProgramsForItem(item)
      programs = programs.concat(itemPrograms)

      if (channels[item.channel.xmltv_id]) continue
      const channel = api.channels.find({ id: item.channel.xmltv_id })
      if (channel) {
        channels[item.channel.xmltv_id] = {
          xmltv_id: item.channel.xmltv_id,
          name: item.channel.display_name,
          logo: channel.icon,
          site: item.channel.site,
          number: channel.Number
        }
      }
    }
    channels = Object.values(channels)
    channels = _.sortBy(channels, 'number')
    programs = _.sortBy(programs, ['channel', 'start'])
    total += programs.length

    const filepath = `${PUBLIC_DIR}/guides/${key}.epg.xml`
    const output = unescapeHTML(grabber.convertToXMLTV({ channels, programs }))
    await file.create(filepath, output)
    const compressed = await zip.compress(output)
    await file.create(filepath + '.gz', compressed)
  }

  if (!total) {
    logger.error('\nError: No programs found')
    process.exit(1)
  } else {
    logger.info(`Done`)
  }
}

main()

function groupByGroup(items = []) {
  const groups = {}

  items.forEach(item => {
    item.groups.forEach(key => {
      if (!groups[key]) {
        groups[key] = []
      }

      groups[key].push(item)
    })
  })

  return groups
}

var htmlEntities = {
  nbsp: ' ',
  cent: '¢',
  pound: '£',
  yen: '¥',
  euro: '€',
  copy: '©',
  reg: '®',
  //lt: '<',
  //gt: '>',
  quot: '"',
  //amp: '&',
  apos: '\''
};

function unescapeHTML(str) {
  return str.replace(/\&([^;]+);/g, function (entity, entityCode) {
      var match;

      if (entityCode in htmlEntities) {
          return htmlEntities[entityCode];
          /*eslint no-cond-assign: 0*/
      } else if (match = entityCode.match(/^#x([\da-fA-F]+)$/)) {
          return String.fromCharCode(parseInt(match[1], 16));
          /*eslint no-cond-assign: 0*/
      } else if (match = entityCode.match(/^#(\d+)$/)) {
          return String.fromCharCode(~~match[1]);
      } else {
          return entity;
      }
  });
};

async function loadQueue() {
  logger.info('Loading queue...')

  await db.queue.load()

  return await db.queue.find({}).sort({ xmltv_id: 1 })
}

async function loadProgramsForItem(item) {
  return await db.programs.find({ _qid: item._id }).sort({ channel: 1, start: 1 })
}
