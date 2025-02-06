#!/usr/local/bin/perl
# Show hosts in BIND cluster
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text);

require './bind8-lib.pl';
$access{'secondarys'} || &error($text{'secondarys_ecannot'});
&foreign_require("servers", "servers-lib.pl");
&ReadParse();
&ui_print_header(undef, $text{'secondarys_title'}, "");

# Show existing servers
my @servers = &list_secondary_servers();
if (@servers) {
	print &ui_form_start("secondary_delete.cgi", "post");
	my @links = ( &select_all_link("d"),
		   &select_invert_link("d") );
	print &ui_links_row(\@links);
	my @tds = ( "width=5" );
	print &ui_columns_start([
		"",
		$text{'secondarys_host'},
		$text{'secondarys_dosec'},
		$text{'secondarys_view'},
		$text{'secondarys_desc'},
		$text{'secondarys_os'} ], 100, 0, \@tds);
	foreach my $s (@servers) {
		my @cols;
		push(@cols, $s->{'host'}.
			    ($s->{'nsname'} ? " ($s->{'nsname'})" : ""));
		push(@cols, $s->{'sec'} ? $text{'yes'} : $text{'no'});
		push(@cols, $s->{'bind8_view'} eq '*' ?
				"<i>$text{'secondarys_sameview'}</i>" :
			    $s->{'bind8_view'} ?
				$s->{'bind8_view'} :
			        "<i>$text{'secondarys_noview'}</i>");
		push(@cols, $s->{'desc'});
		my ($type) = grep { $_->[0] eq $s->{'type'} }
			       servers::get_server_types();
		push(@cols, $type->[1]);
		print &ui_checked_columns_row(\@cols, \@tds, "d", $s->{'id'});
		}
	print &ui_columns_end();
	print &ui_links_row(\@links);
	print &ui_form_end([ [ "delete", $text{'secondarys_delete'} ] ]);
	print "<p>";
	}
else {
	print "<p>$text{'secondarys_none'}</p>\n";
	}

# Get all Webmin servers and groups
my @allservers = grep { $_->{'user'} } &servers::list_servers();
my %gothost = map { $_->{'id'}, 1 } @servers;
my @addservers = grep { !$gothost{$_->{'id'}} } @allservers;
my @groups = &servers::list_all_groups(\@allservers);

# Show form buttons to add, if any
if (@addservers || @groups) {
	print &ui_form_start("secondary_add.cgi", "post");
	print &ui_table_start($text{'secondarys_header'}, undef, 2);

	# Host or group to add
	@addservers = sort { $a->{'host'} cmp $b->{'host'} } @addservers;
	my @opts = ( );
	if (@addservers) {
		# Add hosts not already in list
		foreach my $s (@addservers) {
			push(@opts, [ $s->{'id'},
				      $s->{'host'}.
				      ($s->{'desc'} ? " ($s->{'desc'})" : "")]);
			}
		}
	@groups = sort { $a->{'name'} cmp $b->{'name'} } @groups;
	if (@groups) {
		# Add groups
		foreach my $g (@groups) {
			push(@opts, [ "group_".$g->{'name'},
				      &text('secondarys_group', $g->{'name'}) ]);
			}
		}
	print &ui_table_row($text{'secondarys_add'},
		&ui_select("server", undef, \@opts));

	# Add to view
	print &ui_table_row($text{'secondarys_toview'},
		&ui_radio("view_def", 1,
			  [ [ 1, $text{'secondarys_noview2'}."<br>" ],
			    [ 2, $text{'secondarys_sameview'}."<br>" ],
			    [ 0, $text{'secondarys_inview'} ] ])." ".
		&ui_textbox("view", undef, 20));

	# Create secondary on secondary?
	print &ui_table_row($text{'secondarys_sec'},
		&ui_yesno_radio("sec", 0));

	# Create all existing primaryprimaryprimarys?
	print &ui_table_row($text{'secondarys_sync'},
		&ui_yesno_radio("sync", 0));

	# NS name
	print &ui_table_row($text{'secondarys_name'},
		&ui_opt_textbox("name", undef, 30, $text{'secondarys_same'}));

	print &ui_table_end();
	print &ui_form_end([ [ undef, $text{'secondarys_ok'} ] ]);
	}
else {
	print "<p>",&text('secondarys_need', '../servers/'),"</p>\n";
	}

&ui_print_footer("", $text{'index_return'});

