require 'json'
require 'net/http'
require 'uri'

PATH = './initial_import'.freeze
IMPORT_DONE = "#{PATH}/import_done".freeze
HEADER = { 'Content-Type' => 'application/json' }.freeze

def es_base_uri
  ENV['ES_BASE_URI'] || 'http://localhost:9200'
end

def upload(content, path)
  uri = URI.parse "#{es_base_uri}/#{path}"
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Put.new(uri.request_uri, HEADER)
  request.body = content
  http.request(request)
end

def to_path(file_name)
  path = file_name
  path.slice!("#{PATH}/")
  path.slice!('.json')
  path
end

def log(response, path)
  http_status = response.code.to_i
  if http_status < 200 || http_status > 299
    $stdout.puts "Could not upload '#{path}'", response.to_s, response.body
    raise Net::HTTPBadResponse
  else
    $stdout.puts "Uploaded '#{path}'."
  end
end

def provision
  # if File.exist?(IMPORT_DONE)
  #   $stdout.puts "Already provisioned. Remove file '#{IMPORT_DONE}' to provision again."
  #   return
  # end

  $stdout.puts "Provisioning '#{es_base_uri}'..."
  file_names = Dir.glob("#{PATH}/**/*.json").sort
  file_names.each do |file_name|
    content = File.read file_name
    path = to_path(file_name)
    response = upload(content, path)
    log response, path
  end

  # File.write(IMPORT_DONE, '')
  $stdout.puts 'Provisioning done.'
end

provision
