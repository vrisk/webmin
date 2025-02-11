#!/usr/local/bin/perl
# save_secondary.cgi
# Save changes to secondary zone options in named.conf
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in);

require './bind8-lib.pl';
&ReadParse();
&error_setup($text{'secondary_err'});

my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $z = &zone_to_config($zone);
my $zconf = $z->{'members'};
my $dom = $zone->{'name'};
my $conf = &get_config();
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});
my $indent = $zone->{'view'} ? 2 : 1;

$access{'ro'} && &error($text{'primary_ero'});
$access{'opts'} || &error($text{'primary_eoptscannot'});
&lock_file(&make_chroot($z->{'file'}));

&save_port_address("primarys", "port", $z, $indent);
&save_opt("max-transfer-time-in", \&mtti_check, $z, $indent);
&save_opt("file", \&file_check, $z, $indent);
&save_choice("check-names", $z, $indent);
&save_choice("notify", $z, $indent);
&save_choice("primaryfile-format", $z, $indent);
&save_addr_match("allow-update", $z, $indent);
&save_addr_match("allow-transfer", $z, $indent);
&save_addr_match("allow-query", $z, $indent);
&save_address("also-notify", $z, $indent);
&flush_file_lines();
&unlock_file(&make_chroot($z->{'file'}));
&webmin_log("opts", undef, $dom, \%in);
&redirect("edit_secondary.cgi?zone=$in{'zone'}&view=$in{'view'}");

sub mtti_check
{
return $_[0] =~ /^\d+$/ ? undef : &text('secondary_emax', $_[0]);
}

sub file_check
{
return $text{'secondary_efile'} if ($_[0] !~ /\S/);
my $file = $_[0];
if ($_[0] !~ /^\//) {
	$file = &base_directory($conf)."/".$file;
	}
return &allowed_zone_file(\%access, $file) ? undef :
	&text('secondary_efile2', $_[0]);
}

