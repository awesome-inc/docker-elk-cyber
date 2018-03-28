require 'json'
require 'net/http'
require 'uri'

# Upload files in a folder to Elasticsearchfolder using http PUT 
class Provision
  def self.call
    Provision.new.provision
  end

  def provision
    # if File.exist?(IMPORT_DONE)
    #   $stdout.puts "Already provisioned. Remove file '#{IMPORT_DONE}' to provision again."
    #   return
    # end

    $stdout.puts "Provisioning '#{es_base_uri}'..."
    file_names = Dir.glob("#{PATH}/**/*.json", File::FNM_DOTMATCH).sort
    file_names.each do |file_name|
      content = File.read file_name
      path = to_path(file_name)
      response = upload(content, path)
      log response, path
    end

    # File.write(IMPORT_DONE, '')
    $stdout.puts 'Provisioning done.'
  end

  private

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

  FILE_TO_URI = {
    '_x_' => '*',
    '_;_' => ':'
  }.freeze

  def to_path(file_name)
    path = file_name
    path.slice!("#{PATH}/")
    path.slice!('.json')
    FILE_TO_URI.each { |k,v| path.sub!(k,v) }
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
end

Provision.call
