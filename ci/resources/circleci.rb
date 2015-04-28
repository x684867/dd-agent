require 'colorize'

def flavors_travis
  flavors = {}
  File.open('.travis.yml', 'r') do |f|
    f.each_line do |line|
      next if line.include? '#'
      if line =~ /TRAVIS_FLAVOR=((\w|_)+)( FLAVOR_VERSION=((\d|\.)+))?/
        if flavors[Regexp.last_match(1)]
          flavors[Regexp.last_match(1)].push(Regexp.last_match(4))
        else
          flavors[Regexp.last_match(1)] = [Regexp.last_match(4)]
        end
      end
    end
  end
  flavors
end

def flavors_duos
  result = []
  flavors_travis.each do |flavor, versions|
    versions.each do |version|
      result.push([flavor, version])
    end
  end
  result
end

def circle_flavors
  total = ENV['CIRCLE_NODE_TOTAL'].to_i
  index = ENV['CIRCLE_NODE_INDEX'].to_i
  flavors_duos.select.with_index { |_, i| i % total == index }.each do |flavor, version|
    ENV['TRAVIS_FLAVOR'] = flavor
    if version.nil?
      ENV.delete('FLAVOR_VERSION')
    else
      ENV['FLAVOR_VERSION'] = version
    end
    puts ">>>>>>>>>>>>> FLAVOR: #{flavor} <<<<<<<<<<<<<".red
    puts ">>>>>>>>>>>>> VERSION: #{version} <<<<<<<<<<<<<".green unless version.nil?
    yield flavor
  end
end

namespace :ci do
  namespace :circleci do
    task :install do |t|
      circle_flavors do |flavor|
        puts
        Rake::Task["ci:#{flavor}:before_install"].reenable
        Rake::Task["ci:#{flavor}:before_install"].invoke
        Rake::Task["ci:#{flavor}:install"].reenable
        Rake::Task["ci:#{flavor}:install"].invoke
      end
      t.reenable
    end

    task :run do |t|
      circle_flavors do |flavor|
        Rake::Task["ci:#{flavor}:before_script"].reenable
        Rake::Task["ci:#{flavor}:before_script"].invoke
        Rake::Task["ci:#{flavor}:script"].reenable
        Rake::Task["ci:#{flavor}:script"].invoke
      end
      t.reenable
    end
  end
end
