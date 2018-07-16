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
$m->get("http://10.92.35.20:8080/jenkins/job/$projname/release/?");
#$m->dump_forms();
$m->form_number(2);
$m->add_header("Referer" => "http://10.92.35.20:8080/job/$projname/release/?");
#$m->field('value', '53B-3', 1);
#$m->field('json', '{"parameter":[{"name":"version","value":"53B-3"},{"name":"addversion","value":"yes"},{"name":"addmanifest","value":"yes"},{"name":"perso","value":"0"}]}');
$m->field('json', "{\"parameter\":[$param_string]}");
$m->click('Submit');
