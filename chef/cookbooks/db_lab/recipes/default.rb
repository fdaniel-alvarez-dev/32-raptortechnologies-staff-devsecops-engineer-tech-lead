directory "/tmp/db_lab" do
  recursive true
  mode "0755"
end

file "/tmp/db_lab/chef_ran.txt" do
  content "db_lab cookbook executed\n"
  mode "0644"
end

