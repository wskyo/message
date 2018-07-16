#!/usr/bin/perl
use strict;
use warnings;
use WWW::Mechanize;

#my $projname = $ARGV[0]
my $projname = shift @ARGV;

my @param_array = ();

foreach my $onearg (@ARGV) {
	if ($onearg =~ m/([^=]+)=([^=]+)/) {
		push(@param_array, "{\"name\":\"$1\",\"value\":\"$2\"}");
	}
}

my $param_string = join(',', @param_array);

my $m = WWW::Mechanize->new();
$m->get('http://10.92.35.20:8080/jenkins/login?from=%2Fjenkins%2F');
$m->form_number(2);
$m->field('j_username', 'xiaoli.luo');
$m->field('j_password', '123');
$m->submit();
$m->get("http://10.92.35.20:8080/jenkins/job/$projname/release/");
#$m->dump_forms();
$m->form_number(2);
$m->add_header("Referer" => "http://10.92.35.20:8080/jenkins/job/$projname/release/");
#$m->field('json', '{"parameter":[{"name":"project","value":"pixi4-35_3g"},{"name":"version","value":"BL16"},{"name":"platform","value":"androidL"},{"name":"cts","value":"10.92.37.21"},{"name":"flashimg","value":"false"},{"name":"autosetting","value":"false"},{"name":"runcts","value":"false"},{"name":"rungts","value":"true"},{"name":"firstrun","value":"YES"},{"name":"fail_count","value":"3"}]}');
$m->field('json', "{\"parameter\":[$param_string]}");
$m->click('Submit');
