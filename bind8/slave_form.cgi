#!/usr/local/bin/perl
# secondary_form.cgi
# A form for creating a new secondary or stub zone
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %config);

require './bind8-lib.pl';
my $type = ($0 =~ /secondary_form/);
$access{'secondary'} || &error($type ? $text{'screate_ecannot1'}
				 : $text{'screate_ecannot2'});
my $conf = &get_config();
&ui_print_header(undef, $type ? $text{'screate_title1'}
			      : $text{'screate_title2'}, "",
		 undef, undef, undef, undef, &restart_links());

# Start of the form
print &ui_form_start("create_secondary.cgi", "post");
print &ui_hidden("type", $type);
print &ui_table_start($type ? $text{'screate_header1'}
			    : $text{'screate_header2'}, "width=100%", 4);

# Forward or reverse?
print &ui_table_row($text{'screate_type'},
	&ui_radio("rev", 0, [ [ 0, $text{'screate_fwd'} ],
			      [ 1, $text{'screate_rev'} ] ]), 3);

# Domain name
print &ui_table_row($text{'screate_dom'},
	&ui_textbox("zone", undef, 60), 3);

# Create in view
my @views = &find("view", $conf);
if (@views) {
	my ($defview) = grep { lc($_->{'values'}->[0]) eq
			    lc($config{'default_view'}) } @views;
	print &ui_table_row($text{'mcreate_view'},
		&ui_select("view", $defview ? $defview->{'index'} : undef,
		  [ map { [ $_->{'index'}, $_->{'values'}->[0] ] }
			grep { &can_edit_view($_) } @views ]), 3);
	}

# Zone file
print &ui_table_row($text{'secondary_file'},
	&ui_radio("file_def", 2, [ [ 1, $text{'secondary_none'} ],
				   [ 2, $text{'secondary_auto'} ],
				   [ 0, &ui_filebox("file", undef, 30) ] ]), 3);

# primary servers
print &ui_table_row($text{'secondary_primaries'},
	&ui_textarea("primaries",
		     join("\n", split(/\s+/, $config{'default_primary'})),
		     4, 30), 3);

# primary port
print &ui_table_row($text{'secondary_primaryport'},
	&ui_opt_textbox("port", undef, 5, $text{'default'},
		        $text{'secondary_primary_port'}), 3);

# Create on secondary servers?
my @servers = grep { $_->{'sec'} } &list_secondary_servers();
if (@servers && $access{'remote'}) {
	print &ui_table_row($text{'primary_onsecondary'},
		&ui_yesno_radio("onsecondary", 1));
	}

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'create'} ] ]);

&ui_print_footer("", $text{'index_return'});

