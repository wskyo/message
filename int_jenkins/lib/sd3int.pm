package sd3int;
require Exporter;
use strict;
use warnings;
use POSIX;
use Getopt::Std;
use Getopt::Long;
use Net::SMTP;
use Net::SMTP_auth;
use MIME::Base64;
use MIME::Lite;
use File::Path;
use DBI;
use Expect;
use Spreadsheet::WriteExcel;

our @ISA     = qw(Exporter);
our @EXPORT  = qw(docmd docmd_noexit arrexists usage docmd_forever docmd_exp docmd_exp_noexit docmd_exp_forever);
our @version = 1.0;

sub docmd
{
	my $ret;
	my $dir = getcwd();
	print("docmd: $dir\$ $_[0]\n");
	$ret = system($_[0]);
	my $retcode = $ret>>8;
	if ($retcode != 0) {
		print("\nError running command: $_[0]\n");
		exit($retcode);
	}
}

sub docmd_noexit
{
	my $ret;
	my $dir = getcwd();
	print("docmd_noexit: $dir\$ $_[0]\n");
	$ret = system($_[0]);
	if ($ret>>8 != 0) {
		print("\nError running command: $_[0]\n");
	}
}

sub docmd_forever
{
	my $ret;
	my $retcode = 1;

	while ($retcode != 0 && $retcode != 130) {
		my $dir = getcwd();
		print("docmd: $dir\$ $_[0]\n");
		$ret = system($_[0]);
		$retcode = $ret>>8;
		if ($retcode != 0) {
			print("\nError running command: $_[0], try again\n");
		}
	}
}

sub usage
{
	my $usage = shift;
	print $usage;
	exit 1;
}

sub docmd_exp
{
	my ($cmd, $log)= @_;

	my $dir = getcwd();
	print("docmd_exp: $dir\$ $cmd\n");

	my $exp = new Expect;
	if (defined($log)) {
		$exp->log_file($log);
	}
	$exp->spawn($cmd);
	$exp->expect(undef);
	$exp->log_file(undef);
	my $retcode = $exp->exitstatus()>>8;
	if ($retcode != 0) {
		print("\nError running command: $cmd\n");
		exit($retcode);
	}
}

sub docmd_exp_noexit
{
	my ($cmd, $log)= @_;

	my $dir = getcwd();
	print("docmd_exp_noexit: $dir\$ $cmd\n");

	my $exp = new Expect;
	if (defined $log) {
		$exp->log_file($log);
	}
	$exp->spawn($cmd);
	$exp->expect(undef);
	$exp->log_file(undef);
	my $retcode = $exp->exitstatus()>>8;
	if ($retcode != 0) {
		print("\nError running command: $cmd\n");
	}
}

sub docmd_exp_forever
{
	my ($cmd, $log)= @_;

	my $dir = getcwd();
	print("docmd_exp_forever: $dir\$ $cmd\n");

	my $retcode = 1;

	while ($retcode != 0) {
		my $exp = new Expect;
		if (defined $log) {
			$exp->log_file($log);
		}
		$exp->spawn($cmd);
		$exp->expect(undef);
		$exp->log_file(undef);
		$retcode = $exp->exitstatus()>>8;
		if ($retcode != 0) {
			print("\nError running command: $cmd, try again\n");
		}
	}
}

sub arrexists
{
	my $arr_ref = shift;
	my $item = shift;

	foreach my $ii (@$arr_ref) {
		if ($item eq $ii) {
			return 1;
		}
	}

	return 0;
}
